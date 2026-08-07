"""Модуль клиента для взаимодействия с API Jupyter Server в MLS."""
from uuid import UUID

from mls_core.client import CommonPublicApiInterface


class JupyterServerApi(CommonPublicApiInterface):
    """Выделенный клиент API с логикой взаимодействия с Jupyter Server."""

    _handle_response = CommonPublicApiInterface._handle_api_response

    @_handle_response
    def get_config(self):
        """Конфигурация Jupyter Service: регионы, instance types и образы."""
        return self.get('configs', params={'cluster_type': 'MT'})

    @_handle_response
    def get_jupyter_servers_list(
        self,
        notebook_type: str | None = None,
        order_by: str | None = None,
        desc: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        search: str | None = None,
        status: str | None = None,
        access_mode: str | None = None,
    ):
        """Список Jupyter Server в workspace."""
        params = {
            'notebook_type': notebook_type,
            'order_by': order_by,
            'desc': desc,
            'limit': limit,
            'offset': offset,
            'search': search,
            'status': status,
            'access_mode': access_mode,
        }
        return self.get('notebooks/v2/notebooks', params=params)

    @_handle_response
    def create_jupyter_server(self, namespace: str, payload: dict):
        """Создание Jupyter Server."""
        return self.post(f'notebooks/v2/{namespace}/notebook', json=payload)

    @_handle_response
    def delete_jupyter_server(self, jupyter_server_uuid: UUID):
        """Удаление Jupyter Server."""
        return self.delete(f'notebooks/v2/notebook/{jupyter_server_uuid}')

    @_handle_response
    def pause_jupyter_server(self, jupyter_server_uuid: UUID):
        """Пауза Jupyter Server."""
        return self.post(f'notebooks/v2/notebook/{jupyter_server_uuid}/pause')

    @_handle_response
    def modify_jupyter_server(self, jupyter_server_uuid: UUID, payload: dict):
        """Изменение параметров Jupyter Server."""
        return self.post(f'notebooks/v2/notebook/{jupyter_server_uuid}/modify', json=payload)

    @_handle_response
    def get_workspace_autoshutdown_rule(self, workspace_id: UUID):
        """Получение workspace-правила autoshutdown."""
        return self.get(f'notebooks/v2/autoshutdown-rules/workspace/{workspace_id}')

    @_handle_response
    def set_workspace_autoshutdown_rule(self, workspace_id: UUID, payload: dict):
        """Установка workspace-правила autoshutdown."""
        return self.post(f'notebooks/v2/autoshutdown-rules/workspace/{workspace_id}', json=payload)

    @_handle_response
    def get_jupyter_server(self, jupyter_server_uuid: UUID):
        """Получение Jupyter Server по UUID."""
        return self.get(f'notebooks/v1/notebook/{jupyter_server_uuid}')

    @_handle_response
    def resume_jupyter_server(self, namespace: str, jupyter_server_uuid: UUID, payload: dict):
        """Возобновление Jupyter Server."""
        return self.post(f'notebooks/v1/{namespace}/notebook/{jupyter_server_uuid}/resume', json=payload)

    @_handle_response
    def delete_workspace_autoshutdown_rule(self, workspace_id: UUID):
        """Удаление workspace-правила autoshutdown."""
        return self.delete(f'notebooks/v1/autoshutdown-rules/workspace/{workspace_id}')
