```markdown
# mls

`mls` — это CLI утилита, которая позволяет управлять вашими ML Space продуктами.

## Доступные продукты

- **Jobs**
- **Datatransfer**

## Установка пакета

### Установка через `pip`


```bash
pip install --extra-index-url https://gitverse.ru/api/packages/cloudru/pypi/simple/ mls
```

### Установка через `Poetry` из репозитория Gitverse

Для установки пакета `mls` из вашего внутреннего репозитория Gitverse, выполните следующие шаги:

1. **Добавьте ваш репозиторий в конфигурацию Poetry:**

   ```bash
   poetry config repositories.gitverse https://gitverse.ru/api/packages/cloudru/pypi/simple/
   ```

2. **Установите пакет `mls` из репозитория Gitverse:**

   ```bash
   poetry add mls --source gitverse
   ```

   **Примечание:** Убедитесь, что в вашем проекте настроены необходимые аутентификационные токены для доступа к приватному репозиторию. Это можно сделать через переменные окружения или конфигурационные файлы Poetry.

### Установка через `Conda`

Если вы используете `conda`, добавьте канал вашего репозитория и установите пакет:

```bash
conda config --add channels https://gitverse.ru/api/packages/cloudru/pypi/simple/
conda install mls
```

### Установка через PyPI

Если пакет опубликован на публичном PyPI, установите его стандартным способом:

```bash
pip install mls
```

## Файловая структура

```
├── mls
│   ├── cli.py                # Реализует интерфейс командной строки для приложения
│   ├── doc_cli.py            # Генерирует или отображает документацию для CLI
│   ├── manager
│   │   ├── __init__.py       # Инициализирует пакет manager
│   │   ├── configure
│   │   │   ├── __init__.py   # Инициализирует пакет configure
│   │   │   └── _config.py    # Внутренняя логика настройки приложения
│   │   ├── datatransfer
│   │   │   ├── __init__.py    # Инициализирует пакет datatransfer
│   │   │   └── _transfer.py   # Управление процессами передачи данных
│   │   └── job
│   │       ├── __init__.py    # Инициализирует пакет job
│   │       └── _job.py        # Управление задачами 
│   └── settings.py            # Конфигурационные настройки приложения
```

## CI/CD Интеграция

### Пример для GitLab CI/CD

```yaml
stage:
  stage: start-learning-job
  rules:
    - if: $CI_COMMIT_TAG != null
  script:
    - pip install --extra-index-url https://gitverse.ru/api/packages/cloudru/pypi/simple/ mls
     -printf 'api_key\napi_secret\nregion\nworkspaceid\n' | mls configure
    - mls run job -f goodjob.yaml
```

## Пример использования как библиотеки

Пример использования пакета `mls` как библиотеки в вашем Python коде:

```python
from mls.manager import job

name_job = job.run("example_job_name")
job.logs(name_job, stream=True)
2024-03-25T13:35:10Z Job example-job-id is starting...
2024-03-25T13:35:10Z example-job-id-mpimaster-0:1,
2024-03-25T13:35:10Z 🕒 Waiting for workers to be ready... 🕒
2024-03-25T13:35:25Z Connecting to mpimaster-0 ..... Ready ✓
2024-03-25T13:35:25Z 🚀 All workers are READY 🚀
```
