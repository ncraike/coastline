from . import di
from . import aws

def unpack_config_items(raw_config_item):
    items = []
    tags = raw_config_item.get('tags', {})

    if 'vpc' in raw_config_item:
        vpc_spec = raw_config_item['vpc']
        items.append(
                TagByVpcConfig(vpc_spec=vpc_spec, tags=tags))

        for sub_item in raw_config_items.get('subnets', []):
            items.append(
                    TagBySubnetConfig(
                        vpc_spec=vpc_spec,
                        subnet_spec=sub_item.get('subnet'),
                        tags=sub_item.get('tags', {})))
    else:
        items.append(TagWholeRegionConfig(tags))

    return items


@di.dependsOn('config')
def get_tagging_config():
    full_config = di.resolver.unpack(get_tagging_config)
    raw_config_items = full_config['tagging']
    return sum(
            [unpack_config_items(raw_item)
                for raw_item in raw_config_items],
            [])



class TaggingConfigItem:

    def __init__(self, raw_config_item={}, *args, **kwargs):
        self.tags = raw_config_item.get('tags', {})

        super().__init__(*args, **kwargs)

    def check_tags(self):
        pass

    def _walk_taggable_resources(self):
        for resource_source in self.resource_sources:
            yield from resource_source.walk_taggable_resources()

    def apply_tags(self):
        for resource in self._walk_taggable_resources():
            resource.add_tags(self.tags)

class TagConfig:
    def __init__(self, tags={}, *args, **kwargs):
        self.tags = tags
        super().__init__(*args, **kwargs)

    def _init_core_resource(self):
        # XXX TODO Make this give more meaningful info on subclasses
        raise NotImplementedError("Couldn't find core resource")

    @property
    def core_resource(self):
        if self._core_resource is None:
            self._init_core_resource()
        return self._core_resource

    def apply_tags(self):
        for resource in self.core_resource.walk_taggable_resources():
            resource.add_tags(self.tags)

class TagWholeRegionConfig(TagConfig):
    pass

class TagByVpcConfig(TagConfig):

    def __init__(self, vpc_spec=None, *args, **kwargs):
        self.vpc_spec = vpc_spec
        super().__init__(*args, **kwargs)

    def _init_core_resource(self):
        self._core_resource = aws.resources.find_vpc_from_spec(self.vpc_spec)

class TagBySubnetConfig(TagConfig):
    def __init__(self, subnet_spec=None, *args, **kwargs):
        self.vpc_spec = vpc_spec
        super().__init__(*args, **kwargs)

    def _init_core_resource(self):
        self._core_resource = aws.vpc.find_vpc_from_spec(self.vpc_spec)
