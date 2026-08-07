# Tensorboard YAML-примеры

В этом разделе собраны примеры YAML и CLI-вызовов для команд:

- `mls tensorboard create`
- `mls tensorboard get`
- `mls tensorboard modify`
- `mls tensorboard resume`
- `mls tensorboard pause`
- `mls tensorboard delete`
- `mls tensorboard config`

Для `create` и `resume` параметры можно передать через `--config`, через CLI-опции или совместить оба способа.
Если вместе с `--config` переданы отдельные CLI-опции, YAML используется как базовый шаблон, а явно переданные CLI-значения переопределяют соответствующие поля.

## Создание tensorboard

Готовый шаблон в репозитории: `samples/template.tensorboard.create.yaml`.

Справочники:

```bash
mls ws list
mls tensorboard config
```

`config` возвращает регионы, instance types и образы Tensorboard. `ws list` возвращает workspaces с их `namespace`.

```yaml
namespace: default
tensorboard:
  name: my-tensorboard
  image:
    name: cr.ai.cloud.ru/aicloud-tensorboard/tensorboard-server
    tag: latest
    type: datahub
  instance_type: free.0gpu
  region: SR008
  allocation_name: my-allocation
  queue_name: my-queue
  description: tensorboard for training metrics
  pause_at: 45 * * * *
  postponed_pause_enabled: true
  logdir:
    - /home/jovyan/logs
  tensorboard_params:
    --port: "6006"
  s3_buckets:
    - bucket_name: test
      access_rule: ro
  s3_credentials:
    s3_credentials_source: iam-product-sa
    s3_tenant_id: tenant_id
```

Запуск через YAML:

```bash
mls tensorboard create --config ./samples/template.tensorboard.create.yaml
```

Запуск через YAML как базовый шаблон с CLI override:

```bash
mls tensorboard create --config ./samples/template.tensorboard.create.yaml \
  --name tb-prod \
  --instance-type a100.1gpu.40 \
  --region SR008 \
  --logdir /home/jovyan/prod-logs
```

Тот же payload можно собрать без YAML:

```bash
mls tensorboard create \
  --namespace default \
  --name my-tensorboard \
  --image-name cr.ai.cloud.ru/aicloud-tensorboard/tensorboard-server \
  --image-tag latest \
  --image-type datahub \
  --instance-type free.0gpu \
  --region SR008 \
  --allocation-name my-allocation \
  --queue-name my-queue \
  --description "tensorboard for training metrics" \
  --pause-at "45 * * * *" \
  --postponed-pause-enabled \
  --logdir /home/jovyan/logs \
  --tensorboard-params '{"--port":"6006"}' \
  --s3-buckets-json '[{"bucket_name":"test","access_rule":"ro"}]' \
  --s3-credentials-json '{"s3_credentials_source":"iam-product-sa","s3_tenant_id":"tenant_id"}'
```

Обязательные поля create:

- `name`
- `image.name`
- `image.tag`
- `image.type`
- `instance_type`
- `logdir`

`region` можно передать через `--region`, YAML или профиль. `instance_type` не имеет скрытого default: его нужно задать в YAML или CLI.

## Изменение tensorboard

`modify` принимает только CLI-параметры payload:

```bash
mls tensorboard modify 00000000-0000-4000-8000-000000000000 \
  --description "updated tensorboard" \
  --s3-buckets-json '[{"bucket_name":"bucket-a","access_rule":"ro"}]' \
  --s3-credentials-json '{"s3_credentials_source":"not-enabled"}'
```

Получение подробной информации:

```bash
mls tensorboard get 00000000-0000-4000-8000-000000000000
```

## Управление жизненным циклом

Возобновление:

```bash
mls tensorboard resume 00000000-0000-4000-8000-000000000000 \
  --namespace default \
  --region SR008 \
  --instance-type free.0gpu
```

Через YAML:

```yaml
namespace: default
resume:
  region: SR008
  instance_type: free.0gpu
```

```bash
mls tensorboard resume 00000000-0000-4000-8000-000000000000 \
  --config ./samples/template.tensorboard.resume.yaml
```

Через YAML с переопределением instance type из CLI:

```bash
mls tensorboard resume 00000000-0000-4000-8000-000000000000 \
  --config ./samples/template.tensorboard.resume.yaml \
  --instance-type a100.1gpu.40
```

Приостановка:

```bash
mls tensorboard pause 00000000-0000-4000-8000-000000000000
```

Удаление:

```bash
mls tensorboard delete 00000000-0000-4000-8000-000000000000
```

## Полезно проверить

- UUID передаётся в аргументе команды, не в YAML.
- Для `create` и `resume` обязательно передавать `--namespace` при запуске без
  `--config`; при запуске с `--config` ключ `namespace` должен быть в YAML.
- Для `resume` `instance_type` обязателен в CLI или YAML; `region` берётся из CLI, YAML или профиля.
- `get`, `pause`, `delete`, `modify` принимают UUID tensorboard, но соответствующие
  public-api ручки находятся в namespace notebooks.
- Если YAML для `create` или `resume` невалидный, CLI завершится с ошибкой
  чтения конфигурации.
