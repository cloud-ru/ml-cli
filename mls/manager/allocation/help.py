"""Модуль помощи для CLI команд аллокаций MLS."""
import click

from mls.utils.fomatter import CommonGroupFormatter


class AllocationHelp(CommonGroupFormatter):
    """Класс помощи для группы команд аллокаций."""
    HEADING = 'Управление аллокациями.'


class CommandHelp(click.Command):
    """Класс команд с настройкой заголовков."""
    HEADING = ''

    def format_help(self, ctx, formatter):
        """Переопределение вывода помощи."""
        help_ = AllocationHelp
        help_.HEADING = self.HEADING
        help_().format_help(ctx, formatter)


class ListHelp(CommandHelp):
    """Класс помощи при работе со списком доступных аллокаций."""
    HEADING = 'Отображение доступных аллокаций.'


class InstTypesHelp(CommandHelp):
    """Класс помощи при работе со списком доступных инстанс типов."""
    HEADING = 'Отображение доступных инстанс типов в аллокации.'
