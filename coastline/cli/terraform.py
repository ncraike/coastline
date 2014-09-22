import click

from .. import di
from .. import terraform

DEFAULT_CWD = './provision'

@click.group('terraform')
@click.option(
        '--working-dir',
        default=DEFAULT_CWD,
        type=click.Path(
            exists=True,
            dir_okay=True,
            resolve_path=False))
@click.pass_context
def cli(context, working_dir):
    context.obj.tf_working_dir = working_dir

@cli.command()
@click.pass_obj
def plan(obj):
    terraform.plan(
            obj.tf_working_dir)
