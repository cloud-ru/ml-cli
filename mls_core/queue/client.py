"""Модуль клиента для взаимодействия с API очередей MLS."""
from uuid import UUID

from mls_core.client import CommonPublicApiInterface


class QueueApi(CommonPublicApiInterface):
    """Выделенный клиент api содержащий логику взаимодействия с очередями."""

    _handle_response = CommonPublicApiInterface._handle_api_response

    @_handle_response
    def get_list_queues_by_allocation_id(self, allocation_id: str):
        """Список доступных очередей в воркспейсе."""
        return self.get(f'workspaces/v3/{self.workspace_id}/allocations/{allocation_id}/queues')

    @_handle_response
    def get_instance_types_by_queue_id(self, queue_id: UUID):
        """Список доступных инстанс типов в очереди."""
        return self.get(f'queues/{queue_id}/instance-types')
