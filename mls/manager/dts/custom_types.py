"""Модуль custom_types содержит различные вспомогательные определения типов данных."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

from mls.manager.job.custom_types import CustomGroupedOption

S3_LIKE_CONNECTOR_TYPES = ['s3amazon', 's3custom', 's3google']
DB_LIKE_CONNECTOR_TYPES = ['mssql', 'mysql', 'postgresql', 'clickhouse', 'oracledb']
CUSTOM_CONNECTOR_TYPES = [*S3_LIKE_CONNECTOR_TYPES, *DB_LIKE_CONNECTOR_TYPES]
ALL_CONNECTOR_TYPES = [*CUSTOM_CONNECTOR_TYPES, 'nfs', 'nfsprivate', 'nfsshared', 's3evolution']
TARGET_CONNECTOR_TYPES = ['s3mlspace', 's3custom', 'nfs', 'nfsprivate', 'nfsshared', 's3evolution']
STRATEGY = ['write_all', 'append_new', 'sync_all']

DAYS = {1: 'Пн', 2: 'Вт', 3: 'Ср', 4: 'Чт', 5: 'Пт', 6: 'Сб', 7: 'Вс'}
CONNECTOR_FIELD_NAMES = {
    'connector-id': 'ID',
    'workspace-id': 'ID воркспейса',
    'name': 'Имя',
    'source-type': 'Тип',
    'system': 'Системный',
    'status': 'Статус',
    'created': 'Создан',
    'modified': 'Изменен',
    'uid': 'ID владельца',
    'parameters': 'Параметры',
}

CONNECTOR_DEFAULT_FIELDS = {
    'connector-id': 'ID',
    'name': 'Имя',
    'source-type': 'Тип',
    'system': 'Системный',
    'status': 'Статус',
    'created': 'Создан',
    'parameters': 'Параметры',
}

TRANSFER_DEFAULT_FIELDS = {
    'name': 'Правило',
    'transfer-id': 'ID правила переноса',
    'start-at': 'Время запуска (UTC)',
    'schedule': 'Расписание',
}
TRANSFER_FIELD_NAMES = {
    'name': 'Правило',
    'source': 'Источник',
    'destination': 'Место назначения',
    'transfer-id': 'ID правила переноса',
    'strategy': 'Стратегия',
    'start-at': 'Время запуска (UTC)',
    'schedule': 'Расписание',
    'cluster-name': 'Имя кластера',
    'connector-id': 'ID источника',
    'destination-connector-id': 'ID назначения',
    'source-category': 'Тип источника',
    'destination-source-category': 'Тип назначения',
    'description': 'Описание',
}

CONNECTOR_FIELDS = list(CONNECTOR_FIELD_NAMES)


@dataclass
class SQLType:
    """Схема SQL-подобных типов коннекторов."""

    user: str
    password: str
    database: str
    host: str
    port: str


@dataclass
class S3Type:
    """Схема S3-подобных типов коннекторов."""

    endpoint: str
    bucket: str
    access_key_id: str
    security_key: str


@dataclass
class Connector:
    """Модель коннектора."""

    name: str
    parameters: S3Type | SQLType | None


@dataclass
class ConnectorInput(Connector):
    """Модель обновления коннектора."""

    source_type: str | None


class ConnectorTarget(str, Enum):
    """Тип коннектора, который может быть использован в качестве места назначения."""

    s3custom = 's3custom'
    nfs = 'nfs'
    nfs_private = 'nfsprivate'
    nfs_shared = 'nfsshared'
    s3evolution = 's3evolution'


class ConnectorTypes(str, Enum):
    """Все доступные типы коннекторов."""

    postgresql = 'postgresql'
    mssql = 'mssql'
    mysql = 'mysql'
    clickhouse = 'clickhouse'
    oracledb = 'oracledb'
    s3amazon = 's3amazon'
    s3google = 's3google'

    s3custom = 's3custom'
    nfs = 'nfs'
    nfs_private = 'nfsprivate'
    nfs_shared = 'nfsshared'
    s3evolution = 's3evolution'


@dataclass
class CronViewModel:
    """Модель расписания правила переноса."""

    start_at: str | None = datetime.utcnow().isoformat()
    time: str | None = None
    weekdays: List[int] | None = None
    monthdays: List[int] | None = None
    period: float | None = None


@dataclass
class TransferQuery:
    """Модель поля query."""

    source: str | List[str] = '/'
    destination: str = '/'


@dataclass
class Transfer:
    """Модель правила переноса."""

    name: str
    connector_id: UUID | str
    destination_connector_id: UUID | str
    query: TransferQuery
    connector_type: ConnectorTypes
    destination_connector_type: ConnectorTarget
    cluster_name: str
    strategy: str = 'write_all'
    favorite: bool = False
    description: str | None = None
    crontab: dict | None = None


@dataclass
class TransferUpdate:
    """Модель обновления правила переноса."""

    cluster_name: str | None
    connector_id: UUID | str | None
    destination_connector_id: UUID | str | None
    name: str | None
    favorite: bool | None
    strategy: str
    query: TransferQuery | None
    connector_type: ConnectorTypes | None
    destination_connector_type: ConnectorTarget | None

    description: str
    crontab: dict


class TransferCreateRequired(CustomGroupedOption):
    """Класс очередности отображения обязательных опций."""

    GROUP: str = 'Опции обязательные'
    GROUP_INDEX = -9999 - 1


class TransferCreateOptional(CustomGroupedOption):
    """Класс очередности отображения необязательных опций."""

    GROUP: str = 'Опции дополнительные'
    GROUP_INDEX = -9999


class RequiredOptions(CustomGroupedOption):
    """Класс очередности отображения обязательных опций."""
    GROUP: str = 'Опции обязательные'
    GROUP_INDEX = 9


class OptionalOptions(CustomGroupedOption):
    """Класс очередности отображения необязательных опций."""
    GROUP: str = 'Опции дополнительные'
    GROUP_INDEX = 10
