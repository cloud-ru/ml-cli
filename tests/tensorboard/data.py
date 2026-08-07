"""Тестовые данные для интеграционных тестов TensorBoards."""

TENSORBOARD_LIST = {
    'items': [
        {
            'uuid': '11111111-1111-4111-8111-111111111111',
            'name': 'tb-1',
            'status': 'running',
        },
        {
            'uuid': '22222222-2222-4222-8222-222222222222',
            'name': 'tb-2',
            'status': 'paused',
        },
    ],
    'limit': 2,
    'offset': 0,
    'total': 2,
}

ASYNC_RESULT = {
    'process_id': '33333333-3333-4333-8333-333333333333',
    'status': 'queued',
}

CREATE_TENSORBOARD_PAYLOAD = {
    'name': 'tb-cli',
    'image': {
        'name': 'cr.ai.cloud.ru/aicloud-tensorboard/tensorboard-server',
        'tag': 'latest',
        'type': 'datahub',
    },
    'instance_type': 'a100.1gpu.40',
    'region': 'SR008',
    'allocation_name': 'allocation-a',
    'queue_name': 'queue-a',
    'description': 'created from cli',
    'pause_at': '45 * * * *',
    'postponed_pause_enabled': True,
    's3_buckets': [
        {
            'bucket_name': 'bucket-a',
            'access_rule': 'ro',
        },
        {
            'bucket_name': 'bucket-b',
            'access_rule': 'rw',
        },
    ],
    's3_credentials': {
        's3_credentials_source': 'iam-product-sa',
        's3_tenant_id': 'tenant-a',
    },
    'logdir': ['/home/jovyan/logs', '/home/jovyan/test'],
    'tensorboard_params': {'--port': '6006'},
}

TENSORBOARD_DETAIL = {
    'uid': '11111111-1111-4111-8111-111111111111',
    'name': 'tb-1',
    'status': 'running',
    'image': 'cr.ai.cloud.ru/aicloud-tensorboard/tensorboard-server:0.0.1',
    'age': '1d',
    'ageSeconds': '86400',
    'author': 'user',
    'cpu': '',
    'memory': '',
    'namespace': 'default',
    'reason': 'Running',
}

CONFIG_RESPONSE = {
    'regions': [
        {
            'key': 'NEW-MT-REGION',
            'name': 'New MT Region',
            'description': 'Region from Public API config',
            'nfsName': 'nfs-new',
            'instances_types': [
                {
                    'key': 'free.0gpu',
                    'name': 'Free CPU',
                    'images': [],
                    'resource': {
                        'limits': {'cpu': '2', 'memory': '8Gi', 'nvidia.com/gpu': '0'},
                        'requests': {'cpu': '2', 'memory': '8Gi', 'nvidia.com/gpu': '0'},
                    },
                },
            ],
            'ssh': {'url': 'ssh.example.org', 'port': '22'},
        },
    ],
    'datahub_images': [{'name': 'cr.example/tensorboard', 'tags': ['latest']}],
    'custom_images': [],
}
