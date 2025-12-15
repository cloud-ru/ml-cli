"""Модуль помощи для CLI команд очередей MLS."""
import click

from mls.utils.fomatter import CommonGroupFormatter


class QueueHelp(CommonGroupFormatter):
    """Класс помощи для группы команд очередей."""
    HEADING = 'Управление очередями.'


class CommandHelp(click.Command):
    """Класс команд с настройкой заголовков."""
    HEADING = ''

    def format_help(self, ctx, formatter):
        """Переопределение вывода помощи."""
        help_ = QueueHelp
        help_.HEADING = self.HEADING
        help_().format_help(ctx, formatter)


class ListHelp(CommandHelp):
    """Класс помощи при работе со списком доступных ресурсов в очереди."""
    HEADING = 'Отображение доступных очередей.'


class InstTypesHelp(CommandHelp):
    """Класс помощи при работе со списком доступных аллокаций."""
    HEADING = 'Отображение доступных аллокаций.'
