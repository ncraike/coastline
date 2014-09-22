import boto.ec2
from boto.exception import EC2ResponseError

from . import di

INSTANCE_ID_NOT_FOUND = 'InvalidInstanceID.NotFound'

class InstanceNotFound(Exception): pass

def _get_boto_error_type(exception):
    errors = getattr(exception, 'errors')
    if errors:
        return errors[0][0]

@di.dependsOn('config')
@di.dependsOn('secrets')
def get_conn():
    config, secrets = di.resolver.unpack(get_conn)
    return boto.ec2.connect_to_region(
            config['aws']['region'],
            aws_access_key_id=secrets['aws']['access_key_id'],
            aws_secret_access_key=secrets['aws']['secret_access_key'])

def get_all_instances():
    conn = get_conn()
    reservations = conn.get_all_reservations()
    return sum(
            (getattr(r, 'instances', []) for r in reservations), [])

def get_instance_by_id(inst_id):
    conn = get_conn()
    try:
        reservations = conn.get_all_reservations(
                instance_ids=[inst_id])
        return reservations[0].instances[0]

    except EC2ResponseError as e:
        err_type = _get_boto_error_type(e)
        if err_type == INSTANCE_ID_NOT_FOUND:
            raise InstanceNotFound(e.errors[0])
        else:
            raise e

@di.dependsOn('config')
@di.dependsOn('secrets')
def list():
    pass
