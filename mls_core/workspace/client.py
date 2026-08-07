"""Модуль клиента для взаимодействия с API workspaces MLS."""
from mls_core.client import CommonPublicApiInterface


class WorkspaceApi(CommonPublicApiInterface):
    """Выделенный клиент API с логикой взаимодействия с workspaces."""

    _handle_response = CommonPublicApiInterface._handle_api_response

    @_handle_response
    def get_workspaces(self, customer_id: str | None = None):
        """Список workspaces пользователя."""
        params = {'customer_id': customer_id} if customer_id else None
        return self.get('workspaces/v3/', params=params)
