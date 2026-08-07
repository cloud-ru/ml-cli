"""Модуль клиента для взаимодействия с API TensorBoards MLS."""
from uuid import UUID

from mls_core.client import CommonPublicApiInterface


class TensorboardApi(CommonPublicApiInterface):
    """Выделенный клиент api для взаимодействия с TensorBoards."""

    _handle_response = CommonPublicApiInterface._handle_api_response

    _tensorboards_path = 'tensorboards/v2'

    @_handle_response
    def get_config(self):
        """Конфигурация TensorBoard Service: регионы, instance types и образы."""
        return self.get('configs', params={'cluster_type': 'MT'})

    @_handle_response
    def get_tensorboards_list(
        self,
        order_by: str | None = None,
        desc: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        search: str | None = None,
        status: str | None = None,
    ):
        """Список TensorBoards в воркспейсе."""
        params = {
            'order_by': order_by,
            'desc': desc,
            'limit': limit,
            'offset': offset,
            'search': search,
            'status': status,
        }
        return self.get(f'{self._tensorboards_path}/tensorboards', params=params)

    @_handle_response
    def create_tensorboard(self, namespace: str, payload: dict):
        """Создание TensorBoard."""
        return self.post(f'{self._tensorboards_path}/{namespace}/tensorboard', json=payload)

    @_handle_response
    def get_tensorboard(self, tensorboard_uuid: UUID):
        """Получение TensorBoard по UUID."""
        return self.get(f'{self._tensorboards_path}/tensorboard/{tensorboard_uuid}')

    @_handle_response
    def resume_tensorboard(self, namespace: str, tensorboard_uuid: UUID, payload: dict):
        """Возобновление TensorBoard."""
        return self.post(
            f'{self._tensorboards_path}/{namespace}/tensorboard/{tensorboard_uuid}/resume',
            json=payload,
        )

    @_handle_response
    def pause_tensorboard(self, tensorboard_uuid: UUID):
        """Приостановка TensorBoard."""
        return self.post(f'{self._tensorboards_path}/tensorboard/{tensorboard_uuid}/pause')

    @_handle_response
    def delete_tensorboard(self, tensorboard_uuid: UUID):
        """Удаление TensorBoard."""
        return self.delete(f'{self._tensorboards_path}/tensorboard/{tensorboard_uuid}')

    @_handle_response
    def modify_tensorboard(self, tensorboard_uuid: UUID, payload: dict):
        """Изменение TensorBoard."""
        return self.post(f'{self._tensorboards_path}/tensorboard/{tensorboard_uuid}/modify', json=payload)
