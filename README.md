# О пакетах

Репозиторий содержит инструменты разработчика для работы с [Cloud.ru ML Space](https://cloud.ru/docs/aicloud/mlspace/index.html):
- `mls` — CLI-утилита, которая позволяет запускать некоторые сервисы ML Space из терминала.
- `mls-core` — Python-библиотека с открытым исходным кодом для использования некоторых сервисов ML Space в своих проектах (SDK). 

# Установка

Чтобы установить `mls` на локальную машину, в терминале выполните:

```bash
pip install mls --index-url https://gitverse.ru/api/packages/cloudru/pypi/simple/ --extra-index-url https://pypi.org/simple -U
```
![GIF Установка](install.gif)

`mls-core` установится автоматически.

# Примеры использования

## Получение списка задач

```Bash
mls job list
```
![GIF Получение списка задач](list.gif)

## Просмотр логов задачи

```Bash
mls job logs
```
![GIF Просмотр логов задачи](logs.gif)

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
│   ├── cli.py                 # Входная точка CLI (*также как mls)
│   ├── manager                # Отделение CLI от утилит
│   │   ├── configure          # Подкоманда: mls configure
│   │   │   ├── cli.py         # Вход для настройки профиля
│   │   │   ├── help.py        # mls configure --help
│   │   │   └── utils.py       # Логика управления профилем
│   │   └── job                # Подкоманда: mls job
│   │       ├── cli.py         # Вход для задач ML
│   │       ├── custom_types.py# Определения типов задач ML
│   │       ├── help.py        # mls job --help
│   │       └── utils.py       # Логика управления задачами ML
│   └── utils                  # Утилиты для поведения CLI
│       ├── cli_entrypoint_help.py # mls --help
│       ├── common.py          # Общая логика CLI
│       ├── common_types.py    # Кастомизация типаов
│       ├── execption.py       # Исключения CLI
│       ├── fomatter.py        # Кастомизация справки
│       ├── settings.py        # Параметры инициации приложения
│       └── style.py           # Стили вывода CLI
└── mls_core                   # Входная точка SDK
    ├── client.py              # SDK-клиенты
    └── exeptions.py           # Поведение исключений в SDK
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
