"""Тестовые данные для интеграционных тестов workspace."""

WORKSPACES_RESPONSE = {
    'workspaces': [
        {
            'id': '00000000-0000-4000-8000-000000000000',
            'name': 'workspace-a',
            'namespace': 'namespace-a',
            'project_id': '11111111-1111-4111-8111-111111111111',
            'project_name': 'project-a',
            'owner_email': 'owner@example.org',
            'allocations': [
                {
                    'id': '22222222-2222-4222-8222-222222222222',
                    'name': 'allocation-a',
                    'cluster_key': 'NEW-MT-REGION',
                    'cluster_name': 'New MT Region',
                },
            ],
        },
    ],
}
