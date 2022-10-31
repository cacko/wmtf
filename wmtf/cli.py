import click
from click import Command
from wmtf.wm.client import Client


class WMTFCommand(click.Group):

    def list_commands(self, ctx: click.Context) -> list[str]:
        return list(self.commands)


@click.group(cls=WMTFCommand)
def cli():
    """This script showcases different terminal UI helpers in Click."""
    pass


@cli.command('tasks', short_help="My Tasks")
@click.pass_context
def tasks_list(ctx: click.Context):
    """Shows a alabala menu."""
    try:
        tasks = Client.tasks()
        for task in tasks:
            if task.isActive:
                click.echo(click.style(f">> {task.clock_id}{task.clock.value}{task.summary}", fg='red'))
            else:
                click.echo(f"{task.clock_id}{task.clock.value}{task.summary}")
    except FileNotFoundError:
        pass
    except KeyboardInterrupt:
        click.echo(click.style("Bye!", fg='blue'))
