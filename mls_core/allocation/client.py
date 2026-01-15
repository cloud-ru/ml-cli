"""Модуль клиента для взаимодействия с API аллокаций MLS."""
from uuid import UUID

from mls_core.client import CommonPublicApiInterface


class AllocationApi(CommonPublicApiInterface):
    """Выделенный клиент api содержащий логику взаимодействия с аллокациями."""

    _handle_response = CommonPublicApiInterface._handle_api_response

    @_handle_response
    def get_list_allocations(self):
        """Список доступных аллокаций в воркспейсе."""
        return self.get(f'workspaces/v3/{self.workspace_id}/allocations')

    @_handle_response
    def get_instance_types_by_allocation_id(self, allocation_id: UUID):
        """Список доступных инстанс типов в аллокации."""
        return self.get(f'allocations/{allocation_id}/instance-types')
