"""Единая спецификация опций ``mls js create``: Click-декораторы и списки для ``--config``."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .constants import JS_CREATE_INSTANCE_TYPE_HELP
from .constants import JS_IMAGE_TYPE_CHOICE
from .constants import JS_REGION_HELP
from .custom_types import CreateOptions
from .custom_types import ManifestOptions
from .custom_types import RequiredOptions
from mls.manager.notebook_service.cli_options import apply_click_options
from mls.manager.notebook_service.cli_options import build_cli_flags
from mls.manager.notebook_service.cli_options import config_option
from mls.manager.notebook_service.cli_options import create_payload_options
from mls.manager.notebook_service.cli_options import image_name_option
from mls.manager.notebook_service.cli_options import image_tag_option
from mls.manager.notebook_service.cli_options import image_type_option
from mls.manager.notebook_service.cli_options import instance_type_option
from mls.manager.notebook_service.cli_options import name_option
from mls.manager.notebook_service.cli_options import namespace_option
from mls.manager.notebook_service.cli_options import NotebookServiceOptionSpec
from mls.manager.notebook_service.cli_options import region_option


JsCreateOptionSpec = NotebookServiceOptionSpec


def _js_create_option_specs() -> tuple[NotebookServiceOptionSpec, ...]:
    """Порядок как в справке сверху вниз: ``--config`` … ``--s3-credentials-json``."""
    return (
        config_option(
            help_text='Путь к YAML-манифесту с описанием Jupyter Server',
            option_cls=ManifestOptions,
        ),
        namespace_option(
            help_text='Namespace воркспейса, в котором будет запущен Jupyter Server',
            option_cls=RequiredOptions,
        ),
        name_option(
            help_text='Название Jupyter Server',
            option_cls=RequiredOptions,
        ),
        image_name_option(RequiredOptions),
        image_tag_option(RequiredOptions),
        image_type_option(
            help_text='Тип образа, например datahub или custom',
            image_type_choice=JS_IMAGE_TYPE_CHOICE,
            option_cls=RequiredOptions,
        ),
        instance_type_option(
            help_text=JS_CREATE_INSTANCE_TYPE_HELP,
            option_cls=RequiredOptions,
            index=5,
        ),
        region_option(
            help_text=JS_REGION_HELP,
            option_cls=CreateOptions,
        ),
        *create_payload_options('Описание Jupyter Server', CreateOptions),
    )


JS_CREATE_OPTION_SPECS: tuple[JsCreateOptionSpec, ...] = _js_create_option_specs()

CREATE_CLI_PARAM_NAMES: tuple[str, ...] = tuple(s.param_name for s in JS_CREATE_OPTION_SPECS if s.role != 'config')

CREATE_CLI_REQUIRED_PARAM_NAMES: tuple[str, ...] = tuple(s.param_name for s in JS_CREATE_OPTION_SPECS if s.required_cli)


CREATE_CLI_FLAGS: dict[str, str] = build_cli_flags(
    JS_CREATE_OPTION_SPECS,
    {'postponed_pause_enabled': '--postponed-pause-enabled / --no-postponed-pause-enabled'},
)


def apply_js_create_click_options() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Вешает все ``@click.option`` для ``js create`` в порядке, эквивалентном ручным декораторам."""
    return apply_click_options(JS_CREATE_OPTION_SPECS)


__all__ = (
    'CREATE_CLI_FLAGS',
    'CREATE_CLI_PARAM_NAMES',
    'CREATE_CLI_REQUIRED_PARAM_NAMES',
    'JS_CREATE_OPTION_SPECS',
    'apply_js_create_click_options',
)
