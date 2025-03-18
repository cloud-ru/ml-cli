"""Модуль help предоставляет функции для отображения справки в cli.

По сути форматирование вывода помощи.
"""
import click

from mls.utils.fomatter import CommonGroupFormatter


class ConfigureGroupHelp(CommonGroupFormatter):
    """Класс Формат Помощи MLS JOB."""
    HEADING = 'Настройка профиля пользователя:'


class ConfigureHelp(click.Command):
    """Класс помощи для настройки профилей пользователей."""
    HEADING = 'Настройка профиля пользователя:'

    def format_help(self, ctx, formatter):
        """Переопределение вывода помощи."""
        help_ = ConfigureGroupHelp
        help_.HEADING = self.HEADING
        help_().format_help(ctx, formatter)
