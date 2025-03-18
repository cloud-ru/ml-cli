"""Модуль help предоставляет функции для отображения справки в cli.

По сути форматирование вывода помощи.
"""
import click

from mls.utils.fomatter import CommonGroupFormatter


class CommandHelp(click.Command):
    """Класс команд с настройкой заголовков."""
    HEADING = ''

    def format_help(self, ctx, formatter):
        """Переопределение вывода помощи."""
        help_ = JobHelp
        help_.HEADING = self.HEADING
        help_().format_help(ctx, formatter)


class LogHelp(CommandHelp):
    """Класс помощи для получения журнала (log) задачи обучения."""
    HEADING = 'Просмотр логов.'


class KillHelp(CommandHelp):
    """Класс помощи для удаления задачи обучения."""
    HEADING = 'Прекращение работы задачи.'


class StatusHelp(CommandHelp):
    """Класс помощи для отображения статуса задач обучения."""
    HEADING = 'Получение статуса задачи.'


class RunHelp(CommandHelp):
    """Класс помощи для запуска задач обучения."""
    HEADING = 'Запуск задачи.'


class ListHelp(CommandHelp):
    """Класс помощи при работе со списком задач обучения."""
    HEADING = 'Отображение списка задач пользователя.'


class TableHelp(CommandHelp):
    """Класс помощи при работе со списком задач обучения."""
    HEADING = 'Отображение таблицы задач пользователя.'


class ListPodsHelp(CommandHelp):
    """Класс помощи при работе со списком подов задачи обучения."""
    HEADING = 'Отображение списка подов задач пользователя.'


class RestartHelp(CommandHelp):
    """Класс помощи при перезапуске задачи обучения."""
    HEADING = 'Интерфейс перезапуска задачи по имени.'


class JobHelp(CommonGroupFormatter):
    """Класс Формат Помощи MLS JOB."""
    HEADING = 'Управление задачами обучения.'


class YamlHelp(CommandHelp):
    """Класс помощи отображения yaml примера."""
    HEADING = 'Генератор примера yaml файла по типу задачи.'


class TypeHelp(CommandHelp):
    """Класс справочник по типам."""
    HEADING = 'Справочник по типам задач.'


class ClusterHelp(CommandHelp):
    """Класс справочник по типам."""
    HEADING = 'Справочник по кластерам.'
