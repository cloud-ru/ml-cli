"""Модуль exceptions.

Содержит определения core исключений для использования rest client.
"""
import requests


class AuthorizationError(requests.exceptions.HTTPError):
    """Ошибка авторизации пользователя."""


class DataStreamingFailure(Exception):
    """Исключение, обозначающее ошибку потокового чтения данных."""


class InvalidAuthorizationToken(Exception):
    """Ошибка при чтении токена авторизации."""
