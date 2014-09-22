import json

# Currently Secrets class is just a dict sub-class.
#
# A dict-like interface may be all we need, but we use a sub-class so we
# can change construction later, possibly use an IoC container or type
# checking, etc.
class Secrets(dict):

    def __init__(self, *args, file_path=None, **kwargs):
        self.file_path = file_path
        super().__init__(*args, **kwargs)

    # Add a nicer repr which includes the class name and file_path attr
    def __repr__(self):
        return '{cls_name}({parent_repr}, file_path={file_path!r})'.format(
                cls_name=self.__class__.__name__,
                parent_repr=super().__repr__(),
                file_path=self.file_path)

    # Even an "empty" Secrets object is considered "true"
    def __bool__(self):
        return True

def secrets_from_path(secrets_path):
    loaded_json = json.load(open(secrets_path))
    return Secrets(loaded_json, file_path=secrets_path)
