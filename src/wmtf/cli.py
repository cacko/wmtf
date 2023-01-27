import click
import questionary
from click import Command
from progressor import Spinner, Progress
from pyfiglet import Figlet
from rich import print
from time import sleep
from wmtf.config import app_config
from wmtf.tui.app import Tui
from wmtf.ui.items import MenuItem, TaskItem, DisabledItem
from wmtf.ui.menu import Menu
from wmtf.wm.client import Client
from wmtf.wm import LoginError, MaintenanceError
from wmtf.wm.html.parser import ParserError
from wmtf.wm.models import TaskInfo, ClockLocation
from wmtf.ui.renderables.report import Days as ReportRenderable
from wmtf.ui.renderables.task import Task as TaskRenderable
from random import randint
from typing import Optional
from coretime import seconds_to_duration
import logging
from wmtf.api.server import Server
from wmtf.git import Git
from wmtf.git.message import Message

from time import sleep


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
            MenuItem(text="<< back", obj=main_menu),
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
@click.argument("location", type=click.Choice(["home", "office"], case_sensitive=False))
@click.option("--max-delay", type=int)
def cli_clockoff(ctx: click.Context, location: str, max_delay: Optional[int]):
    tasks = Client.tasks()
    active_task = next(filter(lambda x: x.isActive, tasks), None)
    if not active_task:
        return click.echo(click.style(f"No task is currently active", fg="red"))
    if ClockLocation(location.lower()) != active_task.clock:
        return click.echo(
            click.style(f"active task is not clocked at {location}", fg="red")
        )
    if max_delay:
        interval = randint(1, max(1, max_delay)) * 60
        with Spinner(seconds_to_duration(interval), spinner="arrow3") as sp:
            for counter in range(interval):
                sleep(1)
                sp.update(seconds_to_duration(interval - counter))
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


@cli.command("api-serve", short_help="Start api server")
@click.pass_context
def cli_api_server(ctx: click.Context):
    api_server = Server()
    api_server.start()


def run():
    from wmtf.config import app_config

    try:
        if not app_config.is_configured():
            assert validate_credentials()
        cli()
    except AssertionError:
        pass

def select_task(title:str) -> TaskInfo:
    try:
        click.clear()
        banner(txt=title, fg="blue")
        menu_items = [
            TaskItem(text=f"{task.summary}", obj=task) for task in Client.tasks() if task.group
        ] + [questionary.Separator(), MenuItem(text="exit", obj=quit)]
        with Menu(menu_items, title="Select task") as item:  # type: ignore
            return item.obj
    except ParserError as e:
        click.echo(click.style(e, fg="red"))




@cli.command('branch', short_help="Create branch")
@click.pass_context
def cli_branch(ctx: click.Context):
    """List tasks currently assigned to you and creates a branch from the name of it"""
    task = select_task("create branch")
    assert task
    branch_name = Git.branchName(task)
    Git.checkout("master")
    if questionary.confirm(f"About to create branch \"{branch_name}\""):
        res = Git.checkout(branch_name)
        click.echo(click.style(res, fg='green'))
        quit()

@cli.command('commit')
@click.option('-d', "--dry-run", default=False, is_flag=True)
@click.option('-t', '--commit-type',
              type=click.Choice(['ML', 'Random', 'Default', 'Manual'], case_sensitive=False), default="Default")
def cli_commit(dry_run, commit_type):
    task = select_task("commit to")
    assert task
    match (commit_type.lower()):
        case "default":
            msg = Message.branch(task)
        case "ml":
            msg = Message.summarize(Git.patch())
        case "random":
            msg = Message.random()
        case _:
            msg = questionary.text("commit message: ").ask()

    if dry_run:
        print(msg)
        return

    r = Git.mergeTask(task, "--squash")
    click.echo(click.style(r, fg='green'))

    r = Git.commit(msg)
    click.echo(click.style(r, fg='green'))


if __name__ == "__main__":
    run()
