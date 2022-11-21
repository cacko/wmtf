import click
import questionary
from click import Command
from crontab import CronTab
from progressor import Spinner
from pyfiglet import Figlet
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from time import sleep
from wmtf.config import app_config
from wmtf.tui.app import Tui
from wmtf.ui.items import MenuItem, TaskItem, DisabledItem
from wmtf.ui.menu import Menu
from wmtf.wm.client import Client
from wmtf.wm.html.login import LoginError, MaintenanceError
from wmtf.wm.html.parser import ParserError
from wmtf.wm.models import TaskInfo
from wmtf.ui.renderables.report import Days as ReportRenderable
from wmtf.ui.renderables.task import Task as TaskRenderable



def banner(txt: str, fg: str = "green", bold=True):
    logo = Figlet(width=120).renderText(text=txt)
    click.echo(click.style(logo, fg=fg, bold=bold))


def validate_credentials() -> bool:
    questions = [
        {
            "type": "text",
            "name": "wm.username",
            "message": "Username:",
            "validate": lambda x: len(x.strip()) > 0,
        },
        {
            "type": "password",
            "name": "wm.password",
            "message": "Password:",
            "validate": lambda x: len(x.strip()) > 0,
        },
    ]
    for k, v in questionary.prompt(questions).items():
        app_config.set(k, v)
    try:
        Client.validate_setup()
        click.echo(click.style(f"Credentials are valid", fg="green"))
        return True
    except LoginError as e:
        click.echo(click.style(e, fg="red"))
    return False


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context):
    if ctx.invoked_subcommand is None:
        Tui().run()


@cli.command("quit")
def quit():
    """Quit."""
    click.echo(click.style("Bye!", fg="blue"))
    import sys
    sys.exit(0)


@cli.command("menu", short_help="Menu")
@click.pass_context
def main_menu(ctx: click.Context):
    """Shows a main menu."""
    try:
        click.clear()
        banner(txt="work manager")
        menu_items = [
            MenuItem(text="My Tasks", obj=cli_tasks),
            MenuItem(text="My Report", obj=cli_report),
            MenuItem(text="Settings", obj=cli_settings),
        ] + [MenuItem(text="Exit", obj=quit)]
        with Menu(menu_items) as item:
            match item.obj:
                case Command():
                    ctx.invoke(item.obj)
    except KeyboardInterrupt:
        click.echo(click.style("Bye!", fg="blue"))


@cli.command("settings", short_help="App settings")
@click.pass_context
def cli_settings(ctx: click.Context):
    """Set usernames and passwords"""
    try:
        click.clear()
        banner(txt="settings", fg="yellow")
        menu_items = [
            MenuItem(text=f"{txt}", obj=task)
            for txt, task in [
                ("Credentials", cli_credentials),
            ]
        ] + [
            DisabledItem(disabled=f"config dir", text=f"{app_config.config_dir}"),
            DisabledItem(disabled=f"cache dir", text=f"{app_config.cache_dir}"),
            DisabledItem(disabled=f"data dir", text=f"{app_config.data_dir}"),
            MenuItem(text="<< back", obj=main_menu)
            ]
        with Menu(menu_items, title="Select task") as item:
            match item.obj:
                case Command():
                    ctx.invoke(item.obj)
                case TaskInfo():
                    ctx.forward(cli_task, task_id=item.obj.id)
    except ParserError as e:
        click.echo(click.style(e, fg="red"))


@cli.command("credentials", short_help="Set credentials")
@click.pass_context
def cli_credentials(ctx: click.Context):
    click.clear()
    banner(txt="credentials", fg="magenta")
    valid = validate_credentials()
    click.pause()
    if parent := ctx.parent:
        if parent != ctx.find_root():
            click.clear()
            ctx.invoke(parent.command)
        else:
            return valid


@cli.command("tasks", short_help="My Tasks")
@click.pass_context
def cli_tasks(ctx: click.Context):
    """List issues currently assigned to you and creates a branch from the name of it"""
    try:
        click.clear()
        banner(txt="my tasks", fg="blue")
        menu_items = [
            TaskItem(text=f"{task.summary}", obj=task) for task in Client.tasks()
        ] + [questionary.Separator(), MenuItem(text="back", obj=main_menu)]
        with Menu(menu_items, title="Select task") as item:  # type: ignore
            match item.obj:
                case Command():
                    ctx.invoke(item.obj)
                case TaskInfo():
                    ctx.forward(cli_task, task_id=item.obj.id)
    except ParserError as e:
        click.echo(click.style(e, fg="red"))


@cli.command("task", short_help="Open task")
@click.pass_context
@click.argument("task_id")
def cli_task(ctx: click.Context, task_id: int):
    try:
        task = Client.task(task_id)
        with Spinner("Loading"):
            days = Client.report()
        click.clear()
        banner(txt="Task", fg="blue")
        print(TaskRenderable(task))
    except ParserError as e:
        click.echo(click.style(e, fg="red"))
    click.pause()
    if parent := ctx.parent:
        if parent != ctx.find_root():
            click.clear()
            ctx.invoke(parent.command)


@cli.command("report", short_help="My Report")
@click.pass_context
def cli_report(ctx: click.Context):
    try:
        days = None
        with Spinner("Loading"):
            days = Client.report()
        click.clear()
        banner(txt="my report", fg="red")
        print(ReportRenderable(days))
    except ParserError as e:
        click.echo(click.style(e, fg="red"))
    click.pause()
    if parent := ctx.parent:
        if parent != ctx.find_root():
            click.clear()
            ctx.invoke(parent.command)


@cli.command("clock-off", short_help="Clock off current active task")
@click.pass_context
def cli_clockoff(ctx: click.Context):
    tasks = Client.tasks()
    active_task = next(filter(lambda x: x.isActive, tasks), None)
    if not active_task:
        return click.echo(click.style(f"No task is currently active", fg="red"))

    while True:
        try: 
            click.echo(f">> Trying to clock off task '{active_task.summary}'")
            res = Client.clock_off(active_task.clock_id)
            if res:
                return click.echo(click.style(f"Clocked off", fg="green"))
            else:
                return click.echo(click.style(f"Clock failed", fg="red"))
        except MaintenanceError:
            with Spinner("Maitenance error, retrying in 20 seconds."):
                sleep(20)


@cli.command("cron-clock-off", short_help="Schedule cron to clock off")
@click.pass_context
def cli_cron_clock_off(ctx: click.Context):
    cron = CronTab()
    job = cron.new(command="/home/users/alex.spasov/clock.sh")
    job.schedule()
    cron.write()


def run():
    from wmtf.config import app_config

    try:
        if not app_config.is_configured():
            assert(validate_credentials())    
        cli()
    except AssertionError:
        pass
    
if __name__ == "__main__":
    run()