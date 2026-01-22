# О пакетах

Репозиторий содержит инструменты разработчика для работы с [Cloud.ru Distributed Train](https://cloud.ru/docs/aicloud/mlspace/index.html):
- `mls` — CLI-утилита, которая позволяет запускать некоторые сервисы Distributed Train из терминала.
- `mls-core` — Python-библиотека с открытым исходным кодом для использования некоторых сервисов Distributed Train в своих проектах (SDK).

# Установка

Чтобы установить `mls` на локальную машину, в терминале выполните:

```bash
pip install cloudru-ml-cli==0.11.1
Зеркало: 
pip install --index-url https://gitverse.ru/api/packages/cloudru/pypi/simple/ --extra-index-url https://pypi.org/simple --trusted-host gitverse.ru mls==0.11.1
```
![GIF Установка](https://raw.githubusercontent.com/cloud-ru/ml-cli/refs/heads/master/install.gif)

`mls-core` установится автоматически.

# Перед началом работы

Выполните:

```bash
mls configure
```
![GIF Установка](https://raw.githubusercontent.com/cloud-ru/ml-cli/refs/heads/master/%D0%A1%D0%BF%D1%80%D0%B0%D0%B2%D0%BE%D1%87%D0%BD%D0%B8%D0%BA%20CLI/static/QS6.png)

# Примеры использования

## Получение списка задач

```Bash
mls job list
```
![GIF Получение списка задач](https://raw.githubusercontent.com/cloud-ru/ml-cli/refs/heads/master/list.gif)

## Просмотр логов задачи

```Bash
mls job logs
```
![GIF Просмотр логов задачи](https://raw.githubusercontent.com/cloud-ru/ml-cli/refs/heads/master/logs.gif)

## Запуск задачи через библиотеку

```python
import logging
from mls.utils.common import read_profile
from mls_core import TrainingJobApi, DTSApi, AllocationApi, QueueApi
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    key_id: str
    key_secret: str
    x_workspace_id: str
    x_api_key: str
    region: str
    output: str
    endpoint_url: str


class ManagerApi:
    """Управляющий фасад для доступа ко всем API-сервисам."""

    def __init__(self, settings: Settings, logger: logging.Logger = None):
        client_kwargs = dict(
            endpoint_url=settings.endpoint_url,
            client_id=settings.key_id,
            client_secret=settings.key_secret,
            x_workspace_id=settings.x_workspace_id,
            x_api_key=settings.x_api_key,
            backoff_factor=10,
            connect_timeout=10 * 60,
            read_timeout=10 * 60,
            debug=False
        )
        if logger is not None:
            client_kwargs['logger'] = logger

        self.job = TrainingJobApi(**client_kwargs)
        self.dts = DTSApi(**client_kwargs)
        self.allocation = AllocationApi(**client_kwargs)
        self.queue = QueueApi(**client_kwargs)


if __name__ == "__main__":
    # 1. инициализация logger (1 раз на всё приложение)
    logger = logging.getLogger("my_mlspace_api")
    logger.setLevel(logging.INFO)
    if not logger.handlers:  # чтобы не добавить дважды, если модуль импортируют
        logger.addHandler(logging.StreamHandler())

    # 2. загрузка профиля и создание фасада
    env = read_profile('any_profile_name')
    settings = Settings(**env)
    api = ManagerApi(settings, logger=logger)

    # 3. примеры вызовов:
    print(api.job.run_job(
        payload={
            'script': '/home/jovyan/hello_world.py',
            'base_image': 'cr.ai.cloud.ru/hello_world:latest',
            'instance_type': 'a100.1gpu.40',
            'region': settings.region,
            'type': 'pytorch2',
            'n_workers': 1,
            'job_desc': 'Привет, мир'
        }
    ))
    print(api.dts.transfer_list())
    print(api.dts.conn_sources())
    print(api.allocation.get_list_allocations())
    print(api.queue.get_list_queues_by_allocation_id('00000000-0000-0000-0000-000000000000'))

```
## Файловая структура 
####  Файловая структура не является финальной

```
├── README.md                   # Основная документация проекта.
├── LICENSE                     # Лицензионные условия.
├── install.gif                 # Анимация установки.
├── list.gif                    # Анимация списка.
├── logs.gif                    # Анимация логов.
├── mls
│   ├── cli.py                  # Вход в CLI.
│   ├── manager                 # Логика CLI.
│   │   ├── allocation          # Подкоманда: mls allocation.
│   │   │   ├── cli.py          # Работа с allocation.
│   │   │   └── help.py         # Помощь для allocation.
│   │   ├── configure           # Подкоманда: mls configure.
│   │   │   ├── cli.py          # Настройка профиля.
│   │   │   ├── help.py         # Помощь для configure.
│   │   │   └── utils.py        # Утилиты профиля.
│   │   ├── dts                 # Подкоманда: mls transfer и connector.
│   │   │      ├── connector_cli.py # Работа с connector .
│   │   │      ├── custom_types.py  # Константы и датаклассы .
│   │   │      ├── decorators.py    # Декораторы.
│   │   │      ├── help.py          # Помощь для transfer и connector.
│   │   │      ├── table.py         # Табличное отображение   .
│   │   │      ├── transfer_cli.py  # Работа с transfer. 
│   │   │      └── utils.py         # Утилиты connector и transfer.
│   │   ├── job                  # Подкоманда: mls job.
│   │   │    ├── cli.py          # Управление задачами ML.
│   │   │    ├── constants.py    # Константы   
│   │   │    ├── custom_types.py # Типы задач ML.
│   │   │    ├── dataclasses.py  # Дата-классы задач.
│   │   │    ├── help.py         # Помощь для job.
│   │   │    └── utils.py        # Утилиты задач ML.
│   │   └── queue               # Подкоманда: mls queue.
│   │        ├── cli.py         # Работа с queue.
│   │        └── help.py        # Помощь для queue.
│   └── utils                   # Поддержка CLI.
│       ├── cli_entrypoint_help.py # Помощь CLI.
│       ├── common.py           # Общая логика.
│       ├── client.py           # Обобщение клиента cli (queue и allocation). 
│       ├── common.py           # Общие для cli методы. 
│       ├── common_types.py     # Пользовательские типы.
│       ├── execption.py        # Исключения.
│       ├── fomatter.py         # Форматирование справки.
│       ├── openssl.py          # Поддержка шифрования. 
│       ├── settings.py         # Настройки приложения.
│       └── style.py            # Стили CLI.
├── mls_core                    # SDK ядро.
│   ├── allocation
│   │    └── client.py          # Выделенный клиент allocation. 
│   ├── queue
│   │    └── client.py          # Выделенный клиент queue.
│   ├── client.py               # Клиенты SDK.
│   ├── exeptions.py            # Исключения SDK.
│   └── setting.py              # Настройки SDK.
├── samples
│   ├── template.binary.yaml    # Шаблон бинарных задач.
│   ├── template.binary_exp.yaml# Тестовый шаблон (Нестабильный). TODO 
│   ├── template.horovod.yaml   # Шаблон Horovod.
│   ├── template.pytorch.yaml   # Шаблон PyTorch. (Используйте pytorch2)
│   ├── template.pytorch2.yaml  # Шаблон PyTorch2.(минорно отличается от pytorch)
│   └── template.pytorch_elastic.yaml # Шаблон PyTorch Elastic.
└── Руководство cli
    ├── FAQ.md                  # FAQ.
    ├── Быстрый старт.md        # Быстрый старт.
    ├── Запуск задачи.md        # Запуск задач.
    ├── Работа переменных окружений.md
    ├── Сокрытие credentials.md
    └── Настройка автокомплитера.md # Автозаполнение.

```

# Автокомплитер Zsh

Пользователям Zsh доступна автозаполнение в CLI.
Чтобы использовать опцию, добавьте скрипт ниже в Zsh-профиль:

```bash

_mls_completion() {
    autocomplete "${COMP_WORDS[@]}"
}
complete -F _mls_completion mls

```

Примеры 
> binary YAML  [binary](https://github.com/cloud-ru/ml-cli/blob/master/samples/template.binary.yaml).
> 
> pytorch2 YAML  [pytorch2](https://github.com/cloud-ru/ml-cli/blob/master/samples/template.pytorch2.yaml).
> 
> pytorch_elastic YAML  [pytorch_elastic](https://github.com/cloud-ru/ml-cli/blob/master/samples/template.pytorch_elastic.yaml).

docs: .gitlab-ci.yml rules
