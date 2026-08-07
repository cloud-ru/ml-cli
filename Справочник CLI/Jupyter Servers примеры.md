# Jupyter Server: примеры команд CLI

Команды `mls js create` и `mls js resume` принимают параметры через CLI-опции или YAML-манифест `--config`.
Если вместе с `--config` переданы отдельные CLI-опции, YAML используется как базовый шаблон, а явно переданные CLI-значения переопределяют соответствующие поля.

## Создание Jupyter Server

Перед созданием можно получить конфигурацию Jupyter Service:

```bash
mls ws list
mls js config
```

`mls js config` возвращает регионы, доступные `instance_type`, constraints ресурсов и списки образов из Public API `/configs?cluster_type=MT`. `mls js workspaces` возвращает workspaces с их `namespace` и аллокациями.

Минимальный набор (обязательные поля контракта Public API: `name`, `image`, `instance_type`; `region` можно передать через `--region`, YAML или профиль):

```bash
mls js create --namespace default \
  --name my-js \
  --image-name cr.ai.cloud.ru/aicloud-jupyter/jupyter-server \
  --image-tag 0.0.95 \
  --image-type datahub \
  --instance-type free.0gpu
```

**Регион** — опция `--region` с ключом из `mls js config`. Если опция не передана, используется `region` из YAML, затем регион из профиля.

**Дополнительные поля create** (все опциональны, кроме перечисленных выше обязательных):

| Опция CLI | Поле API |
|-----------|----------|
| `--allocation-name` | `allocation_name` |
| `--queue-name` | `queue_name` |
| `--description` | `description` |
| `--pause-at` | `pause_at` (CRON-строка) |
| `--postponed-pause-enabled` / `--no-postponed-pause-enabled` | `postponed_pause_enabled` (по умолчанию выключено) |
| `--s3-buckets-json` | `s3_buckets` (JSON-массив объектов) |
| `--s3-credentials-json` | `s3_credentials` (JSON-объект) |

Пример с S3 (значения JSON в кавычках в одной строке или через экранирование в shell):

```bash
mls js create --namespace default --name my-js \
  --image-name custom --image-tag v1 --image-type custom --instance-type free.0gpu --region SR006 \
  --s3-buckets-json '[{"bucket_name":"test","access_rule":"ro"}]' \
  --s3-credentials-json '{"s3_credentials_source":"iam-product-sa","s3_tenant_id":"tenant_id"}'
```

В теле запроса всегда передаются `postponed_pause_enabled` (boolean) и `region`; опциональные поля добавляются только если заданы непустые значения (для S3 — если указана соответствующая JSON-опция).

Пример с YAML как базой и CLI override:

```bash
mls js create --config ./samples/template.jupyter_server_create.yaml \
  --name my-js-prod \
  --instance-type a100.1gpu \
  --region SR006
```

## Изменение Jupyter Server (modify)

Нужно указать **хотя бы одно** из изменений: autoshutdown (таймер или полный JSON), описание, S3.

**Autoshutdown**

- `--shutdown-in` + `--timer-enabled` / `--timer-disabled` — короткая форма для `autoshutdown_config.by_timer`.
- `--autoshutdown-config-json` — полный объект `autoshutdown_config` (включая `by_timer`, `by_load`, `by_schedule` по схеме API). Несовместимо с `--shutdown-in`.

**Прочее**

- `--description` — описание notebook.
- `--s3-buckets-json`, `--s3-credentials-json` — как у `create`.

Пример:

```bash
mls js modify 11111111-1111-4111-8111-111111111111 --shutdown-in 3600
mls js modify 11111111-1111-4111-8111-111111111111 --description "Обновлённое описание"
```

## Возобновление Jupyter Server (resume)

Поля тела запроса: `region`, `instance_type`. `instance_type` нужно передать явно через CLI или YAML. `region` берётся из CLI/YAML/профиля.

```bash
mls js resume --namespace default --region SR006 --instance-type free.0gpu \
  11111111-1111-4111-8111-111111111111
mls js resume --config ./samples/template.jupyter_server_resume.yaml \
  --instance-type a100.1gpu 11111111-1111-4111-8111-111111111111
```

## Настройка workspace autoshutdown (autoshutdown set)

Тело запроса: `by_timer`, `by_load`, `by_schedule` (каждое — объект или отсутствует). Нужно указать **хотя бы одно** правило.

- `--shutdown-in` + `--timer-enabled` / `--timer-disabled` — сокращение для объекта `by_timer`.
- `--by-timer-json`, `--by-load-json`, `--by-schedule-json` — полные JSON-объекты соответствующих веток. `--by-timer-json` несовместим с `--shutdown-in`.

```bash
mls js autoshutdown set 00000000-0000-4000-8000-000000000000 --shutdown-in 3600
mls js autoshutdown set 00000000-0000-4000-8000-000000000000 \
  --by-schedule-json '{"shutdown_at":"0 12 * * *","is_enabled":true}'
```

## Полезно проверить

- UUID Jupyter Server передаётся аргументом в `modify`, `pause`, `delete`, `get`, `resume`.
- Для `create` и `resume` обязательный `namespace` передаётся через CLI или YAML.
- Справка по опциям: `mls js <команда> --help`.
