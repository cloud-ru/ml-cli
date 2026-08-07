"""Модуль помощи для CLI-команды workspace."""
import click

from mls.utils.fomatter import CommonGroupFormatter


class Workspace(CommonGroupFormatter):
    """Класс помощи для группы команд workspace."""

    HEADING = 'Управление Workspace.'


class WorkspaceGroupHelp(CommonGroupFormatter):
    """Класс помощи для команды workspace."""

    HEADING = 'Отображение workspaces.'


class WorkspaceHelp(click.Command):
    """Класс помощи для просмотра workspaces."""

    HEADING = 'Отображение workspaces.'

    def format_help(self, ctx, formatter):
        """Переопределение вывода помощи."""
        help_ = WorkspaceGroupHelp
        help_.HEADING = self.HEADING
        help_().format_help(ctx, formatter)
