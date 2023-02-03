import click
import questionary
from click import Command
from progressor import Spinner
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
from wmtf.git import Git, GitError
from wmtf.git.message import Message
import sys
import re


def banner(txt: str, color: str = "bright_green"):
    logo = Figlet(width=120).renderText(text=txt)
    click.secho(logo, fg=color)


def output(txt: str, color="bright_blue"):
    click.secho(txt, fg=color)


def error(e: Exception, txt: Optional[str] = None):
    if not txt:
        txt = f"{e}"
    click.secho(txt, fg="bright_red", err=True)
    if e:
        logging.debug(txt, exc_info=e)


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
        output("Credentials are valid", color="green")
        return True
    except LoginError as e:
        error(e)
    return False


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context):
    if ctx.invoked_subcommand is None:
        Tui().run()


@cli.command("quit")
def quit():
    """Quit."""
    output("Bye!", color="blue")
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
        quit()


@cli.command("settings", short_help="App settings")
@click.pass_context
def cli_settings(ctx: click.Context):
    """Set usernames and passwords"""
    try:
        click.clear()
        banner(txt="settings", color="yellow")
        menu_items = [
            MenuItem(text=f"{txt}", obj=task)
            for txt, task in [
                ("Credentials", cli_credentials),
            ]
        ] + [
            DisabledItem(disabled="config dir",
                         text=f"{app_config.config_dir}"),
            DisabledItem(disabled="cache dir",
                         text=f"{app_config.cache_dir}"),
            DisabledItem(disabled="data dir", text=f"{app_config.data_dir}"),
            MenuItem(text="<< back", obj=main_menu),
        ]
        with Menu(menu_items, title="Select task") as item:
            match item.obj:
                case Command():
                    ctx.invoke(item.obj)
                case TaskInfo():
                    ctx.forward(cli_task, task_id=item.obj.id)
    except ParserError as e:
        error(e, txt="Settings failed")


@cli.command("credentials", short_help="Set credentials")
@click.pass_context
def cli_credentials(ctx: click.Context):
    click.clear()
    banner(txt="credentials", color="magenta")
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
    try:
        click.clear()
        banner(txt="my tasks", color="bright_blue")
        menu_items = [
            TaskItem(text=f"{task.summary}", obj=task)
            for task in Client.tasks()
        ] + [questionary.Separator(), MenuItem(text="back", obj=main_menu)]
        with Menu(menu_items, title="Select task") as item:  # type: ignore
            match item.obj:
                case Command():
                    ctx.invoke(item.obj)
                case TaskInfo():
                    ctx.forward(cli_task, task_id=item.obj.id)
    except ParserError as e:
        error(e)


@cli.command("task", short_help="Open task")
@click.pass_context
@click.argument("task_id")
def cli_task(ctx: click.Context, task_id: int):
    try:
        task = Client.task(task_id)
        with Spinner("Loading"):
            _ = Client.report()
        click.clear()
        banner(txt="Task", color="blue")
        print(TaskRenderable(task))
    except ParserError as e:
        error(e)
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
        banner(txt="my report", color="red")
        print(ReportRenderable(days))
    except ParserError as e:
        error(e)
    click.pause()
    if parent := ctx.parent:
        if parent != ctx.find_root():
            click.clear()
            ctx.invoke(parent.command)


@cli.command("clock-off", short_help="Clock off current active task")
@click.pass_context
@click.argument("location", type=click.Choice(["home", "office"],
                                              case_sensitive=False))
@click.option("--max-delay", type=int)
def cli_clockoff(ctx: click.Context, location: str, max_delay: Optional[int]):
    tasks = Client.tasks()
    active_task = next(filter(lambda x: x.isActive, tasks), None)
    if not active_task:
        return error(Exception("No task is currently active"))
    if ClockLocation(location.lower()) != active_task.clock:
        return error(Exception(f"active task is not clocked at {location}"))
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
                return output("Clocked off")
            else:
                return error(Exception("Clock failed"))
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


def select_task(title: str, only_ids: Optional[list[str]] = None):
    try:
        click.clear()
        banner(txt=title, color="blue")
        menu_items = [
            TaskItem(text=f"{task.summary}", obj=task)
            for task in Client.tasks()
            if task.group and any([only_ids is None or task.id in only_ids])
        ] + [questionary.Separator(), MenuItem(text="exit", obj=quit)]
        with Menu(menu_items, title="Select task") as item:  # type: ignore
            return item.obj
    except ParserError as e:
        error(e)


@cli.command("branch", short_help="Create branch")
@click.pass_context
def cli_branch(ctx: click.Context):
    task = select_task("create branch")
    assert task
    match task:
        case TaskInfo():
            try:
                branch_name = Git.branchName(task)
                Git.checkout("master")
                if questionary.confirm(f'Create "{branch_name}"?'):
                    res = Git.checkout(branch_name)
                    output(res.name)
                    quit()
            except GitError as e:
                error(e)
        case Command():
            ctx.invoke(task)


@cli.command("commit", short_help="Merge a branch")
@click.option("-d", "--dry-run", default=False, is_flag=True)
@click.pass_context
@click.option(
    "-t",
    "--commit-type",
    type=click.Choice(["Random", "Default", "Manual"], case_sensitive=False),
    default="Default",
)
def cli_commit(ctx: click.Context, dry_run, commit_type):
    mr = re.compile(r'^(\d+)-')
    task_ids = []
    for b in Git.branches():
        if m := mr.search(b):
            task_ids.append(int(m.group(1)))
    task = select_task("commit to", task_ids)
    assert task
    match task:
        case TaskInfo():
            try:
                match (commit_type.lower()):
                    case "default":
                        comment = questionary.text("commit message: ").ask()
                        msg = "\n".join([Message.branch(task), comment])
                    case "random":
                        msg = Message.random()
                    case _:
                        msg = questionary.text("commit message: ").ask()

                if dry_run:
                    print(msg)
                    return
                r = Git.mergeTask(task, "--squash")
                output(r)
                r = Git.commit(msg)
            except GitError as e:
                error(e)
        case Command():
            ctx.invoke(task)


if __name__ == "__main__":
    run()
