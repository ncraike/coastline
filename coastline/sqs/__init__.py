from functools import lru_cache

import boto.sqs

from .. import di

@di.dependsOn('config')
@di.dependsOn('secrets')
@di.dependsOn('envstate')
class SqsConfig:

    def __init__(self, *args, **kwargs):
        full_config, secrets, full_state = di.resolver.unpack(SqsConfig)

        self.secrets = secrets

        # Don't store more config or state than we need to
        self.region = full_config['aws']['region']
        self.env_name = full_config.env_name

        self.config = full_config.get('sqs_queues', {})
        self.state = full_state.setdefault('sqs_queues', {})

        self.queues = []
        self._init_queues()

        self.boto_conn = None

        super().__init__(*args, **kwargs)

    def _get_queue_state(self, queue_name):
        for queue_state in self.state.setdefault('queues', []):
            if queue_state['name'] == queue_name:
                return queue_state
        # We couldn't find any state corresponding to the queue name
        else:
            new_state_obj = {'name': queue_name}
            self.state['queues'].append(new_state_obj)
            return new_state_obj


    def _init_queues(self):
        for queue_config in self.config.get('queues', []):
            ConfiguredQueue.check_config(queue_config)
            queue_state = self._get_queue_state(queue_config['name'])

            queue = ConfiguredQueue(
                    queue_config, queue_state, self.env_name,
                    name_prefix=self.config.get('name_prefix'))
            self.queues.append(queue)

    def get_boto_conn(self):
        if self.boto_conn is None:
            self.boto_conn = boto.sqs.connect_to_region(
                    self.region,
                    aws_access_key_id=self.secrets['aws']['access_key_id'],
                    aws_secret_access_key=self.secrets['aws']['secret_access_key']
            )
        return self.boto_conn

    def close_boto_conn(self):
        if self.boto_conn is not None:
            self.boto_conn.close()

    def cleanup(self):
        self.close_boto_conn()

    def status(self):
        conn = self.get_boto_conn()
        try:
            for queue in self.queues:
                if not queue.is_up_to_date:
                    queue.update(conn)
            return self.queues
        finally:
            conn.close()

    def create(self):
        conn = self.get_boto_conn()
        try:
            for queue in self.queues:
                if not queue.is_up_to_date:
                    queue.update(conn)
                if not queue.is_created:
                    queue.create(conn)
            return self.queues
        finally:
            conn.close()

class ConfiguredQueue:

    @classmethod
    def check_config(cls, config):
        if 'name' not in config:
            raise ValueError(
                    "Queue config needs a 'name' attribute",
                    config=config)

    def __init__(
            self, config, state, env_name, *args, name_prefix=None, **kwargs):
        self.check_config(config)

        self.name = config['name']

        self.env_name = env_name
        self.state = state
        self.name_prefix = name_prefix
        self.was_state_outdated = False
        self.was_created_in_this_session = False

        self.is_up_to_date = False

        super().__init__(*args, **kwargs)

    @property
    def url(self):
        return self.state.get('url')

    @property
    def aws_name(self):
        return self.state.get('aws_name')

    @property
    def is_state_complete(self):
        return bool(self.state.get('url') and self.state.get('aws_name'))

    @property
    def is_created(self):
        return bool(self.is_up_to_date and self.is_state_complete)

    def clear_state(self):
        if len(self.state) > 1:
            self.was_state_outdated = True

        self.state.clear()
        self.state['name'] = self.name

    def get_boto_queue(self, boto_conn):
        if not self.is_state_complete:
            return None

        return boto_conn.get_queue(self.state['aws_name'])

    def update(self, boto_conn):
        boto_queue = self.get_boto_queue(boto_conn)
        if boto_queue is None:
            self.clear_state()
            self.is_up_to_date = True
            return

        self.state['url'] = boto_queue.url
        self.is_up_to_date = True

    def _generate_aws_name(self):
        if self.name_prefix:
            return '{prefix}-{env}-{name}'.format(
                prefix=self.name_prefix,
                env=self.env_name,
                name=self.name)
        else:
            return '{env}-{name}'.format(
                env=self.env_name,
                name=self.name)

    def create(self, boto_conn):
        if not self.is_up_to_date:
            raise Exception("update state of queue first")
        if self.is_state_complete:
            raise Exception("queue appears to already have been created")

        boto_queue = boto_conn.create_queue(self._generate_aws_name())
        self.state['aws_name'] = boto_queue.name
        self.state['url'] = boto_queue.url
        self.is_up_to_date = True
        self.was_created_in_this_session = True

@di.dependsOn('config')
def get_configured_queues():
    config = di.resolver.unpack(get_configured_queues)
    return config.get('sqs_queues', [])

def check_configured_queues():
    return [
            dict(queue,
                created=is_queue_created(queue)
            ) for queue in get_configured_queues()
    ]
