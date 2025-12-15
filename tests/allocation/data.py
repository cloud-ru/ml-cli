"""Тестовые данные для интеграционных тестов аллокаций."""

ALLOC_LIST = [
    {
        'id': '00000000-0000-4000-8000-000000000000',
        'name': 'name-1',
        'description': 'description-1',
        'region_key': 'region-1',
    },
    {
        'id': '11111111-1111-4111-9111-111111111111',
        'name': 'name-2',
        'description': 'description-2',
        'region_key': 'region-2',
    },
]

INST_TYPES = [
    {
        'key': 'ke1',
        'name': '1 GPU, 1 CPU-cores, 1 Gb RAM',
        'availability': 0,
    },
    {
        'key': 'ke2',
        'name': '2 GPU, 2 CPU-cores, 2 Gb RAM',
        'availability': 2,
    },
    {
        'key': 'ke1',
        'name': '4 GPU, 4 CPU-cores, 4 Gb RAM',
        'availability': 4,
    },
]
