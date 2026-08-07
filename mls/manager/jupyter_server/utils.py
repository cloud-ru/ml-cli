"""Утилиты CLI Jupyter Server."""
from typing import Any
from typing import Callable

from mls.manager.notebook_service.cli import notebook_service_client
from mls_core import JupyterServerApi


def jupyter_server_api(func: Callable[..., Any]) -> Callable[..., Any]:
    """Декоратор создающий JupyterServerApi instance на базе ввода пользователя."""
    return notebook_service_client(JupyterServerApi)(func)
