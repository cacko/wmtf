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
from wmtf.wm.models import TaskInfo


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
        logo = Figlet(font="poison").renderText(text=f"wmtf")
        click.echo(click.style(logo, fg="green", bold=True))
        menu_items = [
            MenuItem(text="My Tasks", obj=cli_tasks),
            MenuItem(text="My report", obj=cli_report),
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


@cli.command("tasks", short_help="My Tasks")
@click.pass_context
def cli_tasks(ctx: click.Context):
    """List issues currently assigned to you and creates a branch from the name of it"""
    menu_items = [
        TaskItem(text=f"{task.summary}", obj=task) for task in Client.tasks()
    ] + [MenuItem(text="<< back", obj=main_menu)]
    with Menu(menu_items, title="Select task") as item:
        match item.obj:
            case Command():
                ctx.invoke(item.obj)
            case TaskInfo():
                ctx.forward(cli_task, task_id=item.obj.id)


@cli.command("task", short_help="Open task")
@click.pass_context
@click.argument("task_id")
def cli_task(ctx: click.Context, task_id: int):
    task = Client.task(task_id)
    click.clear()
    console = Console()
    parts = [f"# {task.summary}", task.description, "---"]
    if task.comments:
        for c in task.comments:
            parts.append(f"> **{c.author}**\n>\n> {c.comment}")
    console.print(Markdown("\n\n".join(parts)))
    click.pause()
    if parent := ctx.parent:
        if parent != ctx.find_root():
            click.clear()
            ctx.invoke(parent.command)


@cli.command("report", short_help="My Report")
@click.pass_context
def cli_report(ctx: click.Context):
    days = Client.report()
    click.clear()
    parts = []
    for day in days:
        parts = []
        for task in day.tasks:
            parts.append(
                f"- {task.clock_start.strftime('%H:%M')} - {task.clock_end.strftime('%H:%M')} [{task.clock.value}] **{task.summary}** "
            )
        print(Panel(
            Markdown("\n\n".join(parts)), 
            title=f"{day.day.strftime('%A %d %b')}", 
            width=70
            ))
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
