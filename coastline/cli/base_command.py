import click

from .. import di
from .. import config as config_module
from .. import secrets as secrets_module
from .. import envstate as envstate_module

from .helpers import CliState, GroupWithAliasMap
from . import sqs
from . import terraform

DEFAULT_CONFIG_PATH = './config.json'
DEFAULT_ENV = 'development'
DEFAULT_SECRETS_PATH = './secrets.json'
DEFAULT_STATE_PATH = './state.json'

@click.group(
        name='coastline',
        cls=GroupWithAliasMap,
        alias_map={'tf': 'terraform'}
)
@click.option(
        '--config-path', '-c',
        default=DEFAULT_CONFIG_PATH,
        type=click.Path(
            exists=True,
            dir_okay=False,
            resolve_path=False)
)
@click.option(
        '--env', '-e',
        default=DEFAULT_ENV,
        type=click.Choice(config_module.ENV_OPTIONS)
)
@click.option(
        '--secrets-path', '-s',
        default=DEFAULT_SECRETS_PATH,
        type=click.Path(
            exists=True,
            dir_okay=False,
            resolve_path=False)
)
@click.option(
        '--state-path', '-S',
        default=DEFAULT_STATE_PATH,
        type=click.Path(
            exists=True,
            dir_okay=False,
            resolve_path=False)
)
@click.pass_context
def cli(ctx, env, config_path, secrets_path, state_path):
    envstate = envstate_module.envstate_from_path(state_path, env)
    assert envstate
    assert envstate.file_path
    ctx.obj = CliState(
            config=config_module.config_from_path(config_path, env),
            secrets=secrets_module.secrets_from_path(secrets_path),
            envstate=envstate_module.envstate_from_path(state_path, env)
    )

@cli.command()
@di.dependsOn('config')
@di.dependsOn('secrets')
@di.dependsOn('envstate')
def debug():
    config, secrets, envstate = di.resolver.unpack(debug)
    click.echo(config)
    click.echo(secrets)
    click.echo(envstate)

cli.add_command(sqs.cli)
cli.add_command(terraform.cli)
