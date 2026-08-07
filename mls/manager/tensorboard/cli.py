"""Модуль CLI для управления TensorBoards в MLS."""
import uuid
from typing import Any

import click

from .create_cli_options import apply_tensorboard_create_click_options
from .custom_types import ListOptions
from .custom_types import ModifyOptions
from .dataclasses import TensorboardCreateInvocation
from .dataclasses import TensorboardModifyPayload
from .dataclasses import TensorboardResumeInvocation
from .help import ConfigHelp
from .help import CreateHelp
from .help import DeleteHelp
from .help import GetHelp
from .help import ListHelp
from .help import ModifyHelp
from .help import PauseHelp
from .help import ResumeHelp
from .help import TensorboardHelp
from .help import YamlHelp
from .resume_cli_options import apply_tensorboard_resume_click_options
from .utils import tensorboard_api
from .yaml_contract import tensorboard_create_example_yaml
from .yaml_contract import tensorboard_resume_example_yaml
from mls.manager.decorators import opt_output_format
from mls.manager.notebook_service.cli import click_parse_optional_json_array
from mls.manager.notebook_service.cli import click_parse_optional_json_object
from mls.utils.fomatter import ArgumentWithHelpLine
from mls.utils.style import success_format
from mls_core import TensorboardApi


@click.group(cls=TensorboardHelp)
def tensorboard():
    """Группа команд (входная точка) для работы с инстансами TensorBoard.

    Синтаксис: mls tensorboard [command] [args] [options]

    """


@tensorboard.command(cls=YamlHelp)
@click.option(
    '--resume',
    'resume_manifest',
    is_flag=True,
    default=False,
    help='Сгенерировать пример манифеста для перезапуска инстанса TensorBoard',
)
def yaml(resume_manifest: bool):
    """Команда для генерации примера YAML-манифеста для создания или перезапуска инстанса TensorBoard.

    Синтаксис: mls tensorboard yaml [options]

    Пример: mls tensorboard yaml

    Пример: mls tensorboard yaml --resume
    """
    if resume_manifest:
        click.echo(tensorboard_resume_example_yaml(), nl=False)
    else:
        click.echo(tensorboard_create_example_yaml(), nl=False)


@tensorboard.command(cls=ConfigHelp, name='config')
@click.argument(
    'workspace_id',
    required=False,
    cls=ArgumentWithHelpLine,
    type=click.UUID,
    metavar='workspace_id',
)
@opt_output_format
@tensorboard_api
def config(api: TensorboardApi, workspace_id: uuid.UUID | None):
    """Отображает информацию о доступных регионах, инстанс типах и образах для TensorBoard.

    Синтаксис: mls tensorboard config [workspace_id] [options]

    Пример: mls tensorboard config

    Пример: mls tensorboard config 00000000-0000-4000-8000-000000000000

    """
    if workspace_id is not None:
        api.set_workspace_id(workspace_id)
    click.echo(success_format(api.get_config()))


@tensorboard.command(cls=ListHelp, name='list')
@click.option('--order_by', default=None, cls=ListOptions, index=0, help='Поле сортировки инстансов TensorBoard')
@click.option('--desc', is_flag=True, default=False, cls=ListOptions, index=1, help='Сортировка по убыванию инстансов TensorBoard')
@click.option(
    '--limit',
    type=int,
    default=15,
    cls=ListOptions,
    index=2,
    help='Максимальное количество записей в результате выборки',
)
@click.option(
    '--offset',
    type=int,
    default=0,
    cls=ListOptions,
    index=3,
    help='Смещение выборки для пагинации результатов',
)
@click.option(
    '--search',
    default=None,
    cls=ListOptions,
    index=4,
    help='Поиск по названию инстанса TensorBoard для фильтрации результатов',
)
@click.option(
    '--status',
    default=None,
    cls=ListOptions,
    index=5,
    help='Фильтр по статусам инстансов TensorBoard через запятую',
)
@opt_output_format
@tensorboard_api
def list_(
    api: TensorboardApi,
    order_by: str | None,
    desc: bool,
    limit: int | None,
    offset: int | None,
    search: str | None,
    status: str | None,
):
    """Команда отображения списка инстансов TensorBoard.

    Синтаксис: mls tensorboard list [options]

    Пример: mls tensorboard list --status Running --limit 10

    """
    click.echo(
        success_format(
            api.get_tensorboards_list(
                desc=desc,
                limit=limit,
                offset=offset,
                search=search,
                status=status,
                order_by=order_by,
            ),
        ),
    )


@tensorboard.command(cls=GetHelp, name='get')
@click.argument(
    'tensorboard_uuid',
    cls=ArgumentWithHelpLine,
    type=click.UUID,
    metavar='tensorboard_uuid',
)
@opt_output_format
@tensorboard_api
def get_(api: TensorboardApi, tensorboard_uuid: uuid.UUID):
    """Команда для получения подробной информации об инстансе TensorBoard по его уникальному идентификатору (UUID).

    Синтаксис: mls tensorboard get [tensorboard_uuid] [options]

    Пример: mls tensorboard get 11111111-1111-4111-8111-111111111111

    """
    click.echo(success_format(api.get_tensorboard(tensorboard_uuid)))


@tensorboard.command(cls=CreateHelp, name='create')
@apply_tensorboard_create_click_options()
@opt_output_format
@tensorboard_api
def create(api: TensorboardApi, **kwargs: Any):  # noqa: D207
    """Команда для создания инстанса TensorBoard.

    Синтаксис: mls tensorboard create [options]

    Пример: mls tensorboard create --namespace default --name tensorboard-example --image-tag latest
--image-type datahub --image-name cr.ai.cloud.ru/aicloud-tensorboard/tensorboard-server
--instance-type free.0gpu --logdir /home/jovyan/logs

    Пример: mls tensorboard create --config ./samples/template.tensorboard.create.yaml

    """
    config_path = kwargs.pop('config', None)
    try:
        inv = TensorboardCreateInvocation.resolve(config_path=config_path, **kwargs)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    click.echo(success_format(api.create_tensorboard(inv.namespace, inv.api_body())))


@tensorboard.command(cls=ResumeHelp, name='resume')
@apply_tensorboard_resume_click_options()
@click.argument(
    'tensorboard_uuid',
    cls=ArgumentWithHelpLine,
    type=click.UUID,
    metavar='tensorboard_uuid',
)
@opt_output_format
@tensorboard_api
def resume(api: TensorboardApi, **kwargs: Any):
    """Команда перезапуска инстанса TensorBoard.

    Синтаксис: mls tensorboard resume [tensorboard_uuid] [options]

    Пример: mls tensorboard resume 00000000-0000-0000-0000-000000000000 --namespace default --region SR008 --instance-type free.0gpu

    Пример: mls tensorboard resume 00000000-0000-0000-0000-000000000000 --config ./samples/template.tensorboard.resume.yaml

    """
    tensorboard_uuid = kwargs.pop('tensorboard_uuid')
    config_path = kwargs.pop('config', None)
    try:
        inv = TensorboardResumeInvocation.resolve(config_path=config_path, **kwargs)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc

    click.echo(
        success_format(
            api.resume_tensorboard(
                namespace=inv.namespace,
                tensorboard_uuid=tensorboard_uuid,
                payload=inv.resume.to_api_dict(),
            ),
        ),
    )


@tensorboard.command(cls=PauseHelp, name='pause')
@click.argument(
    'tensorboard_uuid',
    cls=ArgumentWithHelpLine,
    type=click.UUID,
    metavar='tensorboard_uuid',
)
@opt_output_format
@tensorboard_api
def pause(api: TensorboardApi, tensorboard_uuid: uuid.UUID, *_, **__):
    """Команда остановки инстанса TensorBoard.

    Синтаксис: mls tensorboard pause [tensorboard_uuid] [options]

    Пример: mls tensorboard pause 00000000-0000-0000-0000-000000000000

    """
    click.echo(success_format(api.pause_tensorboard(tensorboard_uuid)))


@tensorboard.command(cls=DeleteHelp, name='delete')
@click.argument(
    'tensorboard_uuid',
    cls=ArgumentWithHelpLine,
    type=click.UUID,
    metavar='tensorboard_uuid',
)
@opt_output_format
@tensorboard_api
def delete(api: TensorboardApi, tensorboard_uuid: uuid.UUID, *_, **__):
    """Команда удаления инстанса TensorBoard.

    Синтаксис: mls tensorboard delete [tensorboard_uuid] [options]

    Пример: mls tensorboard delete 00000000-0000-0000-0000-000000000000

    """
    click.echo(success_format(api.delete_tensorboard(tensorboard_uuid)))


@tensorboard.command(cls=ModifyHelp, name='modify')
@click.argument(
    'tensorboard_uuid',
    cls=ArgumentWithHelpLine,
    type=click.UUID,
    metavar='tensorboard_uuid',
)
@click.option(
    '--shutdown-in',
    type=int,
    default=None,
    cls=ModifyOptions,
    index=0,
    help=(
        'Время до автовыключения в секундах при отсутствии активности. '
        'Альтернатива параметру --autoshutdown-config-json'
    ),
)
@click.option(
    '--timer-enabled/--timer-disabled',
    default=True,
    cls=ModifyOptions,
    index=1,
    help=(
        'Включение или отключение правила автовыключения по времени. '
        'Обязателен при использовании --shutdown-in. Допустимые варианты: true, false'
    ),
)
@click.option(
    '--autoshutdown-config-json',
    default=None,
    callback=click_parse_optional_json_object,
    cls=ModifyOptions,
    index=2,
    help='JSON-конфигурация автовыключения. Включает правила по времени, расписанию и нагрузке',
)
@click.option('--description', default=None, cls=ModifyOptions, index=3, help='Описание инстанса TensorBoard')
@click.option(
    '--s3-buckets-json',
    default=None,
    callback=click_parse_optional_json_array,
    cls=ModifyOptions,
    index=4,
    help='JSON-массив настроек S3 хранилищ, например [{"bucket_name":"b","access_rule":"ro"}]',
)
@click.option(
    '--s3-credentials-json',
    default=None,
    callback=click_parse_optional_json_object,
    cls=ModifyOptions,
    index=5,
    help='JSON-объект настроек авторизации S3',
)
@opt_output_format
@tensorboard_api
def modify(
    api: TensorboardApi,
    tensorboard_uuid: uuid.UUID,
    shutdown_in: int | None,
    timer_enabled: bool,
    autoshutdown_config_json: dict | None,
    description: str | None,
    s3_buckets_json: list | None,
    s3_credentials_json: dict | None,
):
    """Команда изменения инстанса TensorBoard.

    Синтаксис: mls tensorboard modify [tensorboard_uuid] [options]

    Пример: mls tensorboard modify 00000000-0000-0000-0000-000000000000 --description "Описание"

    """
    try:
        payload = TensorboardModifyPayload.resolve(
            shutdown_in=shutdown_in,
            timer_enabled=timer_enabled,
            autoshutdown_config_json=autoshutdown_config_json,
            description=description,
            s3_buckets=s3_buckets_json,
            s3_credentials=s3_credentials_json,
        ).to_api_dict()
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    click.echo(success_format(api.modify_tensorboard(tensorboard_uuid, payload)))
