"""Тестовые данные для интеграционных тестов Jupyter Server."""

JUPYTER_SERVER_LIST = {
    'items': [
        {
            'uuid': '11111111-1111-4111-8111-111111111111',
            'name': 'nb-1',
            'status': 'running',
            'access_mode': 'private',
        },
        {
            'uuid': '22222222-2222-4222-8222-222222222222',
            'name': 'nb-2',
            'status': 'paused',
            'access_mode': 'shared',
        },
    ],
    'limit': 2,
    'offset': 0,
    'total': 2,
}

JUPYTER_SERVER_DETAIL = {
    'uuid': '11111111-1111-4111-8111-111111111111',
    'name': 'nb-1',
    'status': 'running',
}

ASYNC_RESULT = {
    'process_id': '33333333-3333-4333-8333-333333333333',
    'status': 'queued',
}

AUTOSHUTDOWN_RULE = {
    'by_timer': {
        'shutdown_in': 3600,
        'is_enabled': True,
    },
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
    'datahub_images': [{'name': 'cr.example/jupyter', 'tags': ['latest']}],
    'custom_images': [],
}
