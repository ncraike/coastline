import json
from . import config

# Currently EnvState class is just a dict sub-class.
#
# A dict-like interface may be all we need, but we use a sub-class so we
# can change construction later, possibly use an IoC container or type
# checking, etc.
class EnvState(dict):

    def __init__(self, *args, file_path=None, env_name=None, **kwargs):
        self.file_path = file_path
        self.env_name = env_name
        super().__init__(*args, **kwargs)

    # Add a nicer repr which includes the class name and extra attrs
    def __repr__(self):
        return ('{cls_name}('
                    '{parent_repr}, '
                    'file_path={file_path!r}, '
                    'env_name={env_name!r})'
                ).format(
                    cls_name=self.__class__.__name__,
                    parent_repr=super().__repr__(),
                    file_path=self.file_path,
                    env_name=self.env_name)

    # Even an "empty" EnvState object is considered "true"
    def __bool__(self):
        return True

def envstate_from_path(state_path, env_name):
    json_tree = json.load(open(state_path))
    subtree = json_tree.get(env_name, {})
    return EnvState(subtree, file_path=state_path, env_name=env_name)

def save_envstate_to_path(envstate, state_path, env_name):
    if not state_path:
        raise ValueError("Need a valid state_path, not {!r}".format(state_path))
    if not env_name:
        raise ValueError("Need a valid env_name, not {!r}".format(env_name))

    with open(state_path, 'r') as f:
        json_tree = json.load(f)

    json_tree[env_name] = dict(envstate)

    with open(state_path, 'w') as f:
        json.dump(json_tree, f, indent=4, sort_keys=True)
