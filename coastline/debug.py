import os

from . import di

from . import config as config_module
from . import secrets as secrets_module
from . import envstate as envstate_module

DEFAULT_BASE_PATH = '.'

from .cli.base_command import (
        DEFAULT_CONFIG_PATH,
        DEFAULT_ENV,
        DEFAULT_SECRETS_PATH,
        DEFAULT_STATE_PATH)

def use_default_config_files(base_path='.', env=DEFAULT_ENV):
    from .cli import base_command

    config = config_module.config_from_path(
            os.path.join(base_path, DEFAULT_CONFIG_PATH), env)
    secrets = secrets_module.secrets_from_path(
            os.path.join(base_path, DEFAULT_SECRETS_PATH))
    envstate = envstate_module.envstate_from_path(
            os.path.join(base_path, DEFAULT_STATE_PATH), env)

    di.providers.register_instance(config, 'config')
    di.providers.register_instance(secrets, 'secrets')
    di.providers.register_instance(envstate, 'envstate')
