"""Тестовые данные для интеграционных тестов очереди."""

QUEUE_LIST = [
    {
        'id': '22222222-2222-4222-a222-222222222222',
        'name': 'default',
        'description': 'description1',
        'allocation_id': '00000000-0000-4000-8000-000000000000',
        'active': 'true',
        'type': 'default',
        'default_for_job': 'true',
        'default_for_notebook': 'true',
    },
    {
        'id': '33333333-3333-4333-b333-333333333333',
        'name': 'shared',
        'description': 'description2',
        'allocation_id': '00000000-0000-4000-8000-000000000000',
        'active': 'true',
        'type': 'shared',
        'default_for_job': 'false',
        'default_for_notebook': 'false',
    },
]

INST_TYPES = [
    {
        'key': 'ke4',
        'name': '4 GPU, 4 CPU-cores, 4 Gb RAM',
        'availability': 4,
    },
    {
        'key': 'ke5',
        'name': '5 GPU, 5 CPU-cores, 5 Gb RAM',
        'availability': 5,
    },
    {
        'key': 'ke6',
        'name': '6 GPU, 6 CPU-cores, 6 Gb RAM',
        'availability': 6,
    },
]
