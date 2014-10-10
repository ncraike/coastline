import re

from .connections import vpc as vpc_connect, ec2 as ec2_connect

from .. import di

VPC_ID_RE = re.compile('^vpc-[0-9a-f]+$')
CIDR_BLOCK_RE = re.compile(
        '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\/[0-9]{1,2}$')

def _instances_from_reservations(reservations):
    return sum(
            (getattr(r, 'instances', []) for r in reservations), [])

def _give_one_result(results):
    if len(results) == 0:
        return None
    elif len(results) == 1:
        return results[0]
    else:
        raise Exception('More than one result')

class Resource:
    pass

class Vpc:
    def __init__(self, boto_vpc=None, *args, **kwargs):
        self.boto_vpc = boto_vpc
        self.add_tags = boto_vpc.add_tags
        self.is_taggable = True
        super().__init__(*args, **kwargs)

    @property
    def instances(self):
        reservations = ec2_connect().get_all_reservations(
                filters={'vpc-id':self.boto_vpc.id})
        return _instances_from_reservations(reservations)

    def walk(self):
        yield self
        yield from self.instances

    def walk_taggable(self):
        filter(
                lambda r : r.is_taggable,
                self.walk())

class Subnet:
    def __init__(self, boto_subnet=None, *args, **kwargs):
        self.boto_subnet = boto_subnet
        self.add_tags = boto_subnet.add_tags


def _find_boto_vpc_by_id(vpc_id):
    results = vpc_connect().get_all_vpcs(
            vpc_ids=[vpc_id]
            )
    return _give_one_result(results)

def _find_boto_vpc_by_cidr_block(vpc_cidr_block):
    results = vpc_connect().get_all_vpcs(
            filters={'cidrBlock': [vpc_cidr_block]}
            )
    return _give_one_result(results)

def find_vpc_from_spec(vpc_spec):
    if VPC_ID_RE.match(vpc_spec):
        boto_vpc = _find_boto_vpc_by_id(vpc_spec)
    elif CIDR_BLOCK_RE.match(vpc_spec):
        boto_vpc = _find_boto_vpc_by_cidr_block(vpc_spec)
    else:
        raise ValueError(
                "Must give VPC ID (eg 'vpc-abcd1234') or CIDR block (eg "
                "'172.1.0.0/16')")

    if boto_vpc is not None:
        return Vpc(boto_vpc=boto_vpc)
    else:
        return None
