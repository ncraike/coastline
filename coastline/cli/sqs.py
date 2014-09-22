import click

from .. import di
from .. import sqs
from .. import envstate as envstate_module

from functools import partial

cli = click.Group('sqs')

CREATED_COLOR = 'green'
NEEDS_CREATING_COLOR = 'yellow'
BAD_STATE_COLOR = 'red'

def get_display_status_color(queue, show_was_state_outdated):
    if queue.is_created:
        return 'created', CREATED_COLOR
    elif show_was_state_outdated and queue.was_state_outdated:
        return 'needs creating (state-file out of date)', BAD_STATE_COLOR
    else:
        return 'needs creating', NEEDS_CREATING_COLOR

def _show_state_out_dated_advice(context):
    click.echo(
"The state-file refers to an SQS queue, but it couldn't be found on AWS. "
"Consider running '{command}' to update the state-file and remove out-dated "
"data."
            "".format(
                command=(context.parent.command_path + ' ' + refresh.name)))

@cli.command()
@click.pass_context
def status(context, show_was_state_outdated=True):
    sqs_config = sqs.SqsConfig()
    for queue in sqs_config.status():
        status, color = get_display_status_color(
                queue, show_was_state_outdated)

        queue_name = click.style(queue.name, fg=color, bold=True)
        queue_status = click.style(': ' + status, fg=color)
        click.echo(queue_name + queue_status)

        if show_was_state_outdated and queue.was_state_outdated:
            _show_state_out_dated_advice(context)

        if queue.is_created:
            click.echo('aws_name: {!r}'.format(queue.aws_name))
            click.echo('url: {!r}'.format(queue.url))
        click.echo()

@cli.command()
@click.pass_context
@di.dependsOn('envstate')
def refresh(context):
    envstate = di.resolver.unpack(refresh)

    context.forward(status, show_was_state_outdated=False)

    envstate_module.save_envstate_to_path(
            envstate,
            envstate.file_path,
            envstate.env_name)

@cli.command()
@di.dependsOn('envstate')
def create():
    envstate = di.resolver.unpack(create)

    sqs_config = sqs.SqsConfig()
    queues = sqs_config.status()
    existing_queues = [q for q in queues if q.is_created]
    need_creating = [q for q in queues if not q.is_created]

    if existing_queues:
        queue_names = ', '.join(q.name for q in existing_queues)
        click.echo(
                click.style("Existing queues: ", bold=True, fg=CREATED_COLOR) +
                click.style(queue_names, fg=CREATED_COLOR))
        click.echo()

    if need_creating:
        queue_names = ', '.join(q.name for q in need_creating)
        click.echo(
                click.style("Creating: ", bold=True, fg=NEEDS_CREATING_COLOR) +
                click.style(queue_names, fg=NEEDS_CREATING_COLOR))
        click.echo()

        sqs_config.create()
        for queue in need_creating:
            click.secho(
                    'Created {}'.format(queue.name),
                    fg=CREATED_COLOR, bold=True)
            click.echo('aws_name: {!r}'.format(queue.aws_name))
            click.echo('url: {!r}'.format(queue.url))
            click.echo()
    else:
        click.secho(
                "No queues need creating",
                fg=CREATED_COLOR, bold=True)

    envstate_module.save_envstate_to_path(
            envstate,
            envstate.file_path,
            envstate.env_name)

#
# Debug commands:
#

debug_cli = click.Group('debug')
cli.add_command(debug_cli)

@debug_cli.command()
@di.dependsOn('config')
def all_aws_queues():
    config = di.resolver.unpack(show_all_remote)

    click.echo(
            "Showing all created AWS queues in the {region} region:".format(
                region=config['region']))
    for queue in sqs.get_conn().get_all_queues():
        click.echo(repr(queue))
