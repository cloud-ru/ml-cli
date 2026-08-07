"""Модуль CLI для управления Jupyter Server в MLS."""
import uuid
from typing import Any

import click

from .create_cli_options import apply_js_create_click_options
from .custom_types import AutoShutdownOptions
from .custom_types import ListOptions
from .custom_types import ModifyOptions
from .dataclasses import JupyterServerCreateInvocation
from .dataclasses import JupyterServerModifyPayload
from .dataclasses import JupyterServerResumeInvocation
from .dataclasses import WorkspaceAutoshutdownSetPayload
from .help import AutoShutdownDeleteHelp
from .help import AutoShutdownGetHelp
from .help import AutoShutdownHelp
from .help import AutoShutdownSetHelp
from .help import ConfigHelp
from .help import CreateHelp
from .help import DeleteHelp
from .help import GetHelp
from .help import JupyterServer
from .help import ListHelp
from .help import ModifyHelp
from .help import PauseHelp
from .help import ResumeHelp
from .help import YamlHelp
from .resume_cli_options import apply_js_resume_click_options
from .utils import jupyter_server_api
from .yaml_contract import jupyter_server_create_example_yaml
from .yaml_contract import jupyter_server_resume_example_yaml
from mls.manager.decorators import opt_output_format
from mls.manager.notebook_service.cli import click_parse_optional_json_array
from mls.manager.notebook_service.cli import click_parse_optional_json_object
from mls.utils.fomatter import ArgumentWithHelpLine
from mls.utils.style import success_format
from mls_core import JupyterServerApi


@click.group(cls=JupyterServer, name='js')
def js():
    """Группа команд (входная точка) для работы с Jupyter Server.

    Синтаксис: mls js [command] [args] [options]

    """


@js.command(cls=YamlHelp)
@click.option(
    '--resume',
    'resume_manifest',
    is_flag=True,
    default=False,
    help='Сгенерировать пример манифеста для перезапуска Jupyter Server',
)
def yaml(resume_manifest: bool):
    """Команда для генерации примера YAML-манифеста для создания или перезапуска Jupyter Server.

    Синтаксис: mls js yaml [options]

    Пример: mls js yaml

    Пример: mls js yaml --resume

    """
    if resume_manifest:
        click.echo(jupyter_server_resume_example_yaml(), nl=False)
    else:
        click.echo(jupyter_server_create_example_yaml(), nl=False)


@js.command(cls=ConfigHelp, name='config')
@click.argument(
    'workspace_id',
    required=False,
    cls=ArgumentWithHelpLine,
    type=click.UUID,
    metavar='workspace_id',
)
@opt_output_format
@jupyter_server_api
def config(api: JupyterServerApi, workspace_id: uuid.UUID | None):
    """Отображает информацию о доступных регионах, инстанс типах и образах для Jupyter Server.

    Синтаксис: mls js config [workspace_id] [options]

    Пример: mls js config

    Пример: mls js config 00000000-0000-4000-8000-000000000000

    """
    if workspace_id is not None:
        api.set_workspace_id(workspace_id)
    click.echo(success_format(api.get_config()))


@js.command(cls=ListHelp, name='list')
@click.option(
    '--notebook-type',
    default=None,
    cls=ListOptions,
    index=0,
    help='Фильтр по типу Jupyter Server',
)
@click.option('--order_by', default=None, cls=ListOptions, index=1, help='Поле сортировки результатов')
@click.option('--desc', is_flag=True, default=False, cls=ListOptions, index=2, help='Сортировка по убыванию')
@click.option('--limit', type=int, default=None, cls=ListOptions, index=3, help='Максимальное количество записей в результате выборки')
@click.option('--offset', type=int, default=None, cls=ListOptions, index=4, help='Смещение выборки для пагинации результатов')
@click.option(
    '--search',
    default=None,
    cls=ListOptions,
    index=5,
    help='Поиск по названию Jupyter Server для фильтрации результатов',
)
@click.option('--status', default=None, cls=ListOptions, index=6, help='Фильтр по статусам Jupyter Server через запятую')
@click.option('--access_mode', default=None, cls=ListOptions, index=7, help='Фильтр по режимам доступа через запятую')
@opt_output_format
@jupyter_server_api
def list_(
    api: JupyterServerApi,
    notebook_type: str | None,
    order_by: str | None,
    desc: bool,
    limit: int | None,
    offset: int | None,
    search: str | None,
    status: str | None,
    access_mode: str | None,
):
    """Команда отображения списка Jupyter Server.

    Синтаксис: mls js list [options]

    Пример: mls js list --limit 10 --output json

    Пример: mls js list --search demo --status running,paused --order_by name --desc

    """
    click.echo(
        success_format(
            api.get_jupyter_servers_list(
                notebook_type=notebook_type,
                order_by=order_by,
                desc=desc,
                limit=limit,
                offset=offset,
                search=search,
                status=status,
                access_mode=access_mode,
            ),
        ),
    )


@js.command(cls=GetHelp, name='get')
@click.argument(
    'jupyter_server_uuid',
    cls=ArgumentWithHelpLine,
    type=click.UUID,
    metavar='jupyter_server_uuid',
)
@opt_output_format
@jupyter_server_api
def get_(api: JupyterServerApi, jupyter_server_uuid: uuid.UUID):
    """Команда для получения подробной информации о Jupyter Server по его уникальному идентификатору (UUID).

    Синтаксис: mls js get [jupyter_server_uuid] [options]

    Пример: mls js get 11111111-1111-4111-8111-111111111111

    """
    click.echo(success_format(api.get_jupyter_server(jupyter_server_uuid)))


@js.command(cls=CreateHelp, name='create')
@apply_js_create_click_options()
@opt_output_format
@jupyter_server_api
def create(api: JupyterServerApi, **kwargs: Any):
    """Команда для создания и запуска Jupyter Server.

    Синтаксис: mls js create [options]

    Пример: mls js create --namespace default --name my-js --image-name
        cr.ai.cloud.ru/aicloud-jupyter/jupyter-server --image-tag latest --image-type datahub
        --instance-type free.0gpu

    Пример: mls js create --config ./samples/template.jupyter_server_create.yaml

    """
    config_path = kwargs.pop('config', None)
    try:
        inv = JupyterServerCreateInvocation.resolve(config_path=config_path, **kwargs)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    click.echo(success_format(api.create_jupyter_server(inv.namespace, inv.api_body())))


@js.command(cls=DeleteHelp, name='delete')
@click.argument('jupyter_server_uuid', type=click.UUID)
@opt_output_format
@jupyter_server_api
def delete(api: JupyterServerApi, jupyter_server_uuid: uuid.UUID, *_, **__):
    """Команда удаления Jupyter Server.

    Синтаксис: mls js delete [jupyter_server_uuid] [options]

    Пример: mls js delete 11111111-1111-4111-8111-111111111111

    """
    click.echo(success_format(api.delete_jupyter_server(jupyter_server_uuid)))


@js.command(cls=PauseHelp, name='pause')
@click.argument('jupyter_server_uuid', type=click.UUID)
@opt_output_format
@jupyter_server_api
def pause(api: JupyterServerApi, jupyter_server_uuid: uuid.UUID, *_, **__):
    """Команда остановки Jupyter Server.

    Синтаксис: mls js pause [jupyter_server_uuid] [options]

    Пример: mls js pause 11111111-1111-4111-8111-111111111111

    """
    click.echo(success_format(api.pause_jupyter_server(jupyter_server_uuid)))


@js.command(cls=ModifyHelp, name='modify')
@click.argument('jupyter_server_uuid', type=click.UUID)
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
@click.option('--description', default=None, cls=ModifyOptions, index=3, help='Описание Jupyter Server')
@click.option(
    '--s3-buckets-json',
    default=None,
    callback=click_parse_optional_json_array,
    cls=ModifyOptions,
    index=4,
    help=(
        'JSON-массив настроек S3 хранилищ. Например: ``[{"bucket_name":"b","access_rule":"ro"}]``'
    ),
)
@click.option(
    '--s3-credentials-json',
    default=None,
    callback=click_parse_optional_json_object,
    cls=ModifyOptions,
    index=5,
    help=(
        'JSON-объект настроек авторизации S3. По умолчанию на стороне API ``not-enabled``'
    ),
)
@opt_output_format
@jupyter_server_api
def modify(
    api: JupyterServerApi,
    jupyter_server_uuid: uuid.UUID,
    shutdown_in: int | None,
    timer_enabled: bool,
    autoshutdown_config_json: dict | None,
    description: str | None,
    s3_buckets_json: list | None,
    s3_credentials_json: dict | None,
):
    """Команда изменения параметров Jupyter Server.

    Синтаксис: mls js modify [jupyter_server_uuid] [options]

    Пример: mls js modify 11111111-1111-4111-8111-111111111111 --shutdown-in 3600

    Пример: mls js modify 11111111-1111-4111-8111-111111111111 --description "Мой сервер"

    """
    try:
        payload = JupyterServerModifyPayload(
            shutdown_in=shutdown_in,
            timer_enabled=timer_enabled,
            autoshutdown_config_json=autoshutdown_config_json,
            description=description,
            s3_buckets=s3_buckets_json,
            s3_credentials=s3_credentials_json,
        ).to_api_dict()
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    click.echo(success_format(api.modify_jupyter_server(jupyter_server_uuid, payload)))


@js.command(cls=ResumeHelp, name='resume')
@apply_js_resume_click_options()
@click.argument('jupyter_server_uuid', type=click.UUID)
@opt_output_format
@jupyter_server_api
def resume(api: JupyterServerApi, **kwargs: Any):
    """Команда перезапуска Jupyter Server.

    Синтаксис: mls js resume [options] [jupyter_server_uuid]

    Пример: mls js resume --namespace default --region SR004 --instance-type free.0gpu 11111111-1111-4111-8111-111111111111

    Пример: mls js resume --config ./samples/template.jupyter_server_resume.yaml 11111111-1111-4111-8111-111111111111

    """
    jupyter_server_uuid = kwargs.pop('jupyter_server_uuid')
    config_path = kwargs.pop('config', None)
    try:
        inv = JupyterServerResumeInvocation.resolve(config_path=config_path, **kwargs)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    click.echo(
        success_format(
            api.resume_jupyter_server(inv.namespace, jupyter_server_uuid, inv.resume.to_api_dict()),
        ),
    )


@js.group(cls=AutoShutdownHelp, name='autoshutdown')
def autoshutdown():
    """Группа команд для работы с правилами автовыключения Jupyter Server на уровне воркспейса.

    Синтаксис: mls js autoshutdown [command] [args] [options]

    Пример: mls js autoshutdown get 00000000-0000-4000-8000-000000000000

    """


@autoshutdown.command(cls=AutoShutdownGetHelp, name='get')
@click.argument(
    'workspace_id',
    cls=ArgumentWithHelpLine,
    type=click.UUID,
    metavar='workspace_id',
)
@opt_output_format
@jupyter_server_api
def get_workspace_rule(api: JupyterServerApi, workspace_id: uuid.UUID, *_, **__):
    """Команда просмотра правил автовыключения Jupyter Server на уровне воркспейса.

    Синтаксис: mls js autoshutdown get [workspace_id] [options]

    Пример: mls js autoshutdown get 00000000-0000-4000-8000-000000000000

    """
    click.echo(success_format(api.get_workspace_autoshutdown_rule(workspace_id)))


@autoshutdown.command(cls=AutoShutdownSetHelp, name='set')
@click.argument(
    'workspace_id',
    cls=ArgumentWithHelpLine,
    type=click.UUID,
    metavar='workspace_id',
)
@click.option(
    '--shutdown-in',
    type=int,
    default=None,
    cls=AutoShutdownOptions,
    index=0,
    help=(
        'Время до автовыключения в секундах при отсутствии активности. '
        'Несовместим с параметром --by-timer-json'
    ),
)
@click.option(
    '--timer-enabled/--timer-disabled',
    default=True,
    cls=AutoShutdownOptions,
    index=1,
    help=(
        'Включение или отключение правила автовыключения по времени. '
        'Обязателен при использовании --shutdown-in. Допустимые варианты: true, false'
    ),
)
@click.option(
    '--by-timer-json',
    default=None,
    callback=click_parse_optional_json_object,
    cls=AutoShutdownOptions,
    index=2,
    help=(
        'JSON-конфигурация правила автовыключения по времени. '
        'Несовместим с параметром --shutdown-in'
    ),
)
@click.option(
    '--by-load-json',
    default=None,
    callback=click_parse_optional_json_object,
    cls=AutoShutdownOptions,
    index=3,
    help='JSON-конфигурация правила автовыключения по нагрузке',
)
@click.option(
    '--by-schedule-json',
    default=None,
    callback=click_parse_optional_json_object,
    cls=AutoShutdownOptions,
    index=4,
    help='JSON-конфигурация правила автовыключения по расписанию',
)
@opt_output_format
@jupyter_server_api
def set_workspace_rule(
    api: JupyterServerApi,
    workspace_id: uuid.UUID,
    shutdown_in: int | None,
    timer_enabled: bool,
    by_timer_json: dict | None,
    by_load_json: dict | None,
    by_schedule_json: dict | None,
):
    """Команда создания или обновления правил автовыключения Jupyter Server на уровне воркспейса.

    Синтаксис: mls js autoshutdown set [workspace_id] [options]

    Пример: mls js autoshutdown set 00000000-0000-4000-8000-000000000000 --shutdown-in 3600

    """
    if by_timer_json is not None and shutdown_in is not None:
        raise click.UsageError('Нельзя одновременно указывать --by-timer-json и --shutdown-in')
    by_timer = by_timer_json
    if by_timer is None and shutdown_in is not None:
        by_timer = {'shutdown_in': shutdown_in, 'is_enabled': timer_enabled}
    try:
        payload = WorkspaceAutoshutdownSetPayload(
            by_timer=by_timer,
            by_load=by_load_json,
            by_schedule=by_schedule_json,
        ).to_api_dict()
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    click.echo(success_format(api.set_workspace_autoshutdown_rule(workspace_id, payload)))


@autoshutdown.command(cls=AutoShutdownDeleteHelp, name='delete')
@click.argument(
    'workspace_id',
    cls=ArgumentWithHelpLine,
    type=click.UUID,
    metavar='workspace_id',
)
@opt_output_format
@jupyter_server_api
def delete_workspace_rule(api: JupyterServerApi, workspace_id: uuid.UUID, *_, **__):
    """Команда удаления правил автовыключения Jupyter Server на уровне воркспейса.

    Синтаксис: mls js autoshutdown delete [workspace_id] [options]

    Пример: mls js autoshutdown delete 00000000-0000-4000-8000-000000000000

    """
    click.echo(success_format(api.delete_workspace_autoshutdown_rule(workspace_id)))
