import click
from click import Command
from crontab import CronTab
from pyfiglet import Figlet
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from wmtf.tui.app import Tui
from wmtf.ui.items import TaskItem
from wmtf.ui.menu import Menu, MenuItem
from wmtf.wm.client import Client
from wmtf.wm.html.parser import ParserError
from wmtf.wm.models import TaskInfo
from progressor import Spinner
from wmtf.config import app_config
import questionary

def banner(txt: str, fg: str = "green", bold=True):
    logo = Figlet(width=120).renderText(text=txt)
    click.echo(click.style(logo, fg=fg, bold=bold))


class WMTFCommand(click.Group):
    def list_commands(self, ctx: click.Context) -> list[str]:
        return list(self.commands)


@click.group(cls=WMTFCommand)
def cli():
    """This script showcases different terminal UI helpers in Click."""
    pass


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
            MenuItem(text="Settings", obj=cli_settings)
        ] + [MenuItem(text="Exit", obj=quit)]
        with Menu(menu_items) as item:
            match item.obj:
                case Command():
                    ctx.invoke(item.obj)
    except KeyboardInterrupt:
        click.echo(click.style("Bye!", fg="blue"))


@cli.command("app", short_help="Start app")
def cli_app():
    Tui().run()

@cli.command("settings", short_help="App settings")
@click.pass_context
def cli_settings(ctx: click.Context):
    """Set usernames and passwords"""
    try:
        click.clear()
        banner(txt="settings", fg='yellow')
        menu_items = [
            MenuItem(text=f"{txt}", obj=task) for txt,task in [
                ("Username", cli_set_username),
                ("Password", cli_set_password),
            ]
        ] + [MenuItem(text="<< back", obj=main_menu)]
        with Menu(menu_items, title="Select task") as item:
            match item.obj:
                case Command():
                    ctx.invoke(item.obj)
                case TaskInfo():
                    ctx.forward(cli_task, task_id=item.obj.id)
    except ParserError as e:
        click.echo(click.style(e, fg="red"))

@cli.command("set-username", short_help="Set username")
@click.pass_context
def cli_set_username(ctx: click.Context):
    value = questionary.text("WM Username:").ask()
    app_config.set("wm.username", value)
    if parent := ctx.parent:
        if parent != ctx.find_root():
            click.clear()
            ctx.invoke(parent.command)   

@cli.command("set-password", short_help="Set password")
@click.pass_context
def cli_set_password(ctx: click.Context):
    value = questionary.password("WM Password:").ask()
    app_config.set("wm.password", value)
    if parent := ctx.parent:
        if parent != ctx.find_root():
            click.clear()
            ctx.invoke(parent.command)   


@cli.command("tasks", short_help="My Tasks")
@click.pass_context
def cli_tasks(ctx: click.Context):
    """List issues currently assigned to you and creates a branch from the name of it"""
    try:
        click.clear()
        banner(txt="my tasks", fg='blue')
        menu_items = [
            TaskItem(text=f"{task.summary}", obj=task) for task in Client.tasks()
        ] + [MenuItem(text="<< back", obj=main_menu)]
        with Menu(menu_items, title="Select task") as item:
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
        click.clear()
        console = Console()
        parts = [f"# {task.summary}", task.description, "---"]
        if task.comments:
            for c in task.comments:
                parts.append(f"> **{c.author}**\n>\n> {c.comment}")
        console.print(Markdown("\n\n".join(parts)))
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
        banner(txt="my report", fg='red')
        parts = []
        for day in days:
            parts = []
            for task in day.tasks:
                parts.append(
                    f"- {task.clock_start.strftime('%H:%M')} - {task.clock_end.strftime('%H:%M')} {task.clock.icon.value} **{task.summary}** "
                )
            print(
                Panel(
                    Markdown("\n\n".join(parts)),
                    title=f"{day.day.strftime('%A %d %b')} / {day.total_display}",
                    width=70,
                )
            )
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

    if active_task:
        click.echo(f">> Trying to clock off task '{active_task.summary}'")
        res = Client.clock_off(active_task.clock_id)
        if res:
            return click.echo(click.style(f"Clocked off", fg="green"))
        else:
            return click.echo(click.style(f"Clock failed", fg="red"))


@cli.command("cron-clock-off", short_help="Schedule cron to clock off")
@click.pass_context
def cli_cron_clock_off(ctx: click.Context):
    cron = CronTab()
    job = cron.new(command="/home/users/alex.spasov/clock.sh")
    job.schedule()
    cron.write()
