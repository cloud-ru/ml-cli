"""Модуль exceptions.

Содержит определения core исключений для использования rest client.
"""
import requests


class AuthorizationError(requests.exceptions.HTTPError):
    """Ошибка авторизации пользователя."""
