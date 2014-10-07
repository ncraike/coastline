from enum import Enum

import boto.ec2
from boto.exception import EC2ResponseError

from . import di

class TagStatus(Enum):
    correct = 1
    incorrect = 2
    missing = 3

INSTANCE_ID_NOT_FOUND = 'InvalidInstanceID.NotFound'

class InstanceNotFound(Exception): pass

def _get_boto_error_type(exception):
    errors = getattr(exception, 'errors')
    if errors:
        return errors[0][0]

def _instances_from_reservations(reservations):
    return sum(
            (getattr(r, 'instances', []) for r in reservations), [])

@di.dependsOn('config')
@di.dependsOn('secrets')
def get_conn():
    config, secrets = di.resolver.unpack(get_conn)
    return boto.ec2.connect_to_region(
            config['aws']['region'],
            aws_access_key_id=secrets['aws']['access_key_id'],
            aws_secret_access_key=secrets['aws']['secret_access_key'])

@di.dependsOn('config')
def get_required_tags():
    config = di.resolver.unpack(get_required_tags)
    return config.get('tags', {})

@di.dependsOn('config')
def get_instances_for_config():
    config = di.resolver.unpack(get_instances_for_config)
    try:
        configured_vpc = config['aws']['vpc']
        return get_instances_in_vpc(configured_vpc)
    except KeyError as e:
        return get_all_instances()

def get_all_instances():
    conn = get_conn()
    reservations = conn.get_all_reservations()
    return _instances_from_reservations(reservations)

def get_instances_in_vpc(vpc_id):
    conn = get_conn()
    reservations = conn.get_all_reservations(
            filters={'vpc-id':vpc_id})
    return _instances_from_reservations(reservations)

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

def instance_tag_status(instance, tag):
    tag_key, tag_value = tag

    if tag_key not in instance.tags:
        return TagStatus.missing

    if instance.tags[tag_key] == tag_value:
        return TagStatus.correct
    else:
        return TagStatus.incorrect

def instance_tags_status(instance, tags):
    return {
            tag_key:
                instance_tag_status(instance, (tag_key, tag_value))
            for tag_key, tag_value in tags.items()}

def get_instances_tags_status(instances, tags):
    return {
            i: instance_tags_status(i, tags)
            for i in instances}
