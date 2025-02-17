# О пакетах

Репозиторий содержит инструменты разработчика для работы с [Cloud.ru ML Space](https://cloud.ru/docs/aicloud/mlspace/index.html):
- `mls` — CLI-утилита, которая позволяет запускать некоторые сервисы ML Space из терминала.
- `mls-core` — Python-библиотека с открытым исходным кодом для использования некоторых сервисов ML Space в своих проектах (SDK). 

# Установка

Чтобы установить `mls` на локальную машину, в терминале выполните:

```bash
pip install mls --index-url https://gitverse.ru/api/packages/cloudru/pypi/simple/ --extra-index-url https://pypi.org/simple -U
```
[GIF Установка](install.gif)

`mls-core` установится автоматически.

# Примеры использования

## Получение списка задач

```Bash
mls job list
```
[GIF Получение списка задач](list.gif)

## Просмотр логов задачи

```Bash
mls job logs
```
[GIF Просмотр логов задачи](logs.gif)

## Запуск задачи через библиотеку

```python
from mls_core import TrainingJobApi

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
#### Внимание: - Файловая структура не является финальной! 

```

├── README.md
├── mls
│         ├── cli.py                       # Входная точка при работе с CLI (*в дальнейшем mls)
│         ├── manager                      # Каталог, отделяющий наполнение CLI от утилит 
│         │         ├── configure          # Подкаталог mls configure
│         │         │         ├── cli.py   # Входная точка при работе с настройкой профиля 
│         │         │         ├── help.py  # Подкаталог mls configure --help 
│         │         │         └── utils.py # Файл, отделяющий логику CLI от функций управления профиля
│         │         └── job                # Подкаталог mls job
│         │             ├── cli.py         # Входная точка при работе с задачами машинного обучения
│         │             ├── custom_types.py# Частные определения типов задачами машинного обучения 
│         │             ├── help.py        # Подкаталог mls job --help 
│         │             └── utils.py       # Файл, отделяющий логику CLI от функций управления задач машинного обучения
│         └── utils                        # Утилиты для управления поведением CLI-приложения 
│             ├── cli_entrypoint_help.py   # Подкаталог mls --help 
│             ├── common.py                # Сценарии, описывающие внешнее поведение CLI 
│             ├── common_types.py          # Сценарии, меняющие внешнее поведение некоторых типов CLI
│             ├── execption.py             # Сценарии, определяющие собственное поведение CLI-исключений
│             ├── fomatter.py              # Сценарии, определяющие собственное поведение отображения справочной информации
│             ├── settings.py              # Сценарии, определяющие параметры инстанциирования приложения  
│             └── style.py                 # Сценарии, определяющие стили вывода в CLI
└── mls_core                               # Входная точка при работе с SDK
    ├── client.py                          # SDK-клиенты 
    └── exeptions.py                       # Сценарии, определяющие собственное поведение SDK-исключений
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
