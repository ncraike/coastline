from functools import update_wrapper

import click

from .. import di
from .. import config as config_module
from .. import secrets as secrets_module
from .. import envstate as envstate_module

class CliState(object):

    def __init__(self, config=None, secrets=None, envstate=None):
        self.config = config or config_module.Config()
        self.secrets = secrets or secrets_module.Secrets()
        self.envstate = envstate or envstate_module.EnvState()

        self._register_resource_providers()

    def _register_resource_providers(self):
        di.providers.register_instance(self.config, 'config')
        di.providers.register_instance(self.secrets, 'secrets')
        di.providers.register_instance(self.envstate, 'envstate')

pass_cli_state = click.make_pass_decorator(CliState)

def make_pass_cli_state_attr_decorator(attr_name):
    def decorator(f):
        @pass_cli_state
        @click.pass_context
        def new_func(ctx, cli_state, *args, **kwargs):
            kwargs[attr_name] = getattr(cli_state, attr_name)
            return ctx.invoke(f, *args, **kwargs)
        return update_wrapper(new_func, f)
    return decorator

# Example:
# pass_my_attr = make_pass_cli_state_attr_decorator('my_attr')

class CommandAliasMapMixin:

    def __init__(self, *args, alias_map=None, **kwargs):
        if alias_map is None: alias_map = {}
        self.alias_map = alias_map

        super().__init__(*args, **kwargs)

    def get_command(self, context, cmd_name, *args, **kwargs):
        # Only activate if normal command resolution can't find anything
        cmd = super().get_command(context, cmd_name, *args, **kwargs)
        if cmd is not None:
            return cmd

        # If the command name is an alias to another command, resolve the
        # command name the alias points to
        aliased_name = self.alias_map.get(cmd_name)
        if aliased_name is not None:
            return self.get_command(context, aliased_name, *args, **kwargs)

        return None

class GroupWithAliasMap(CommandAliasMapMixin, click.Group):
    pass
