# О пакетах

Репозиторий содержит инструменты разработчика для работы с [Cloud.ru ML Space](https://cloud.ru/docs/aicloud/mlspace/index.html):
- `mls` — CLI-утилита, которая позволяет запускать некоторые сервисы ML Space из терминала.
- `mls-core` — Python-библиотека с открытым исходным кодом для использования некоторых сервисов ML Space в своих проектах (SDK).


# Установка

Чтобы установить `mls` на локальную машину, в терминале выполните:


```bash
pip install cloudru-ml-cli==0.6.9
Зеркало: 
pip install --index-url https://gitverse.ru/api/packages/cloudru/pypi/simple/ --extra-index-url https://pypi.org/simple --trusted-host gitverse.ru mls==0.7.3
```
![GIF Установка](https://raw.githubusercontent.com/cloud-ru/ml-cli/refs/heads/feature/add-to-pypi/install.gif)

`mls-core` установится автоматически.

# До использования 

## Выполните 

```bash
mls configure
```
![GIF Установка](https://raw.githubusercontent.com/cloud-ru/ml-cli/refs/heads/feature/add-to-pypi/%D0%A1%D0%BF%D1%80%D0%B0%D0%B2%D0%BE%D1%87%D0%BD%D0%B8%D0%BA%20CLI/static/QS6.png)

# Примеры использования

## Получение списка задач

```Bash
mls job list
```
![GIF Получение списка задач](https://raw.githubusercontent.com/cloud-ru/ml-cli/refs/heads/feature/add-to-pypi/list.gif)

## Просмотр логов задачи

```Bash
mls job logs
```
![GIF Просмотр логов задачи](https://raw.githubusercontent.com/cloud-ru/ml-cli/refs/heads/feature/add-to-pypi/logs.gif)

## Запуск задачи через библиотеку

```python
from mls_core import TrainingJobApi
# Это будет еще переделываться ()

client = TrainingJobApi(
    'https://api.ai.cloud.ru/public/v2',
    'APIKEY_ID',
    'APIKEY_SECRET',
    'WORKSPACE_ID',
    'X_API_KEY'
)
client.run_job(
        payload={
            'script': '/home/jovyan/hello_world.py',
            'base_image': 'cr.ai.cloud.ru/hello_world:latest',
            'instance_type': 'a100.1gpu.40',
            'region': 'REGION',
            'type': 'pytorch2',
            'n_workers': 1,
            'job_desc': 'Привет, мир'
        }
)
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
│   │   ├── configure           # Подкоманда: mls configure
│   │   │   ├── cli.py          # Настройка профиля.
│   │   │   ├── help.py         # Помощь для configure.
│   │   │   └── utils.py        # Утилиты профиля.
│   │   └── job                 # Подкоманда: mls job
│   │       ├── cli.py          # Управление задачами ML.
│   │       ├── custom_types.py # Типы задач ML.
│   │       ├── dataclasses.py  # Дата-классы задач.
│   │       ├── help.py         # Помощь для job.
│   │       └── utils.py        # Утилиты задач ML.
│   └── utils                   # Поддержка CLI.
│       ├── cli_entrypoint_help.py # Помощь CLI.
│       ├── common.py           # Общая логика.
│       ├── common_types.py     # Пользовательские типы.
│       ├── execption.py        # Исключения.
│       ├── fomatter.py         # Форматирование справки.
│       ├── settings.py         # Настройки приложения.
│       └── style.py            # Стили CLI.
├── mls_core                    # SDK ядро.
│   ├── client.py               # Клиенты SDK.
│   ├── exeptions.py            # Исключения SDK.
│   └── setting.py              # Настройки SDK.
├── samples
│   ├── template.binary.yaml    # Шаблон бинарных задач.
│   ├── template.binary_exp.yaml# Тестовый шаблон (Нестабильный). TODO 
│   ├── template.horovod.yaml   # Шаблон Horovod.
│   ├── template.nogpu.yaml     # Шаблон задач без GPU.
│   ├── template.pytorch.yaml   # Шаблон PyTorch. (Используйте pytorch2)
│   ├── template.pytorch2.yaml  # Шаблон PyTorch2.(минорно отличается от pytorch)
│   ├── template.pytorch_elastic.yaml # Шаблон PyTorch Elastic.
│   └── template.spark.yaml     # Шаблон Spark.
└── Руководство cli
    ├── FAQ.md                  # FAQ.
    ├── Быстрый старт.md        # Быстрый старт.
    ├── Запуск задачи.md        # Запуск задач.
    └── Настройка автокомплитера.md # Автозаполнение.

```

# zsh Автокомплитер 

## Пользователям ZSH доступна опция авто заполнения в cli 

### Добавьте скрипт ниже в zsh профиль

```bash

_mls_completion() {
    autocomplete "${COMP_WORDS[@]}"
}
complete -F _mls_completion mls

```

Примеры 
> binary YAML  [binary](./samples/template.binary.yaml).
> 
> pytorch2 YAML  [pytorch2](./samples/template.pytorch2.yaml).
> 
> pytorch_elastic YAML  [pytorch_elastic](./samples/template.pytorch_elastic.yaml).

docs: .gitlab-ci.yml rules
