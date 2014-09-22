import json

BASE_ENV = 'common'
ENV_OPTIONS = ['development', 'staging', 'production']

# Currently Config class is just a dict sub-class.
#
# A dict-like interface may be all we need, but we use a sub-class so we
# can change construction later, possibly use an IoC container or type
# checking, etc.
class Config(dict):

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

    # Even an "empty" Config object is considered "true"
    def __bool__(self):
        return True

def fold_dicts(*dicts):
    if not dicts:
        return None

    result = dicts[0]
    for d in dicts[1:]:
        result.update(d)

    return result

def fold_tree_by_env_name(json_tree, env_name):
    base_tree = json_tree.get(BASE_ENV, {})
    env_tree = json_tree.get(env_name, {})
    return fold_dicts(base_tree, env_tree)

def config_from_path(config_path, env_name):
    json_tree = json.load(open(config_path))
    folded_tree = fold_tree_by_env_name(json_tree, env_name)
    return Config(folded_tree, file_path=config_path, env_name=env_name)
