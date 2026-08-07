"""Модуль помощи для CLI-команд Jupyter Server в MLS."""
import click

from mls.utils.fomatter import CommonGroupFormatter


class JupyterServer(CommonGroupFormatter):
    """Класс помощи для группы команд Jupyter Server."""

    HEADING = 'Управление Jupyter Server.'


class JupyterServerAutoshutdownHelp(CommonGroupFormatter):
    """Класс помощи для группы команд autoshutdown Jupyter Server."""

    HEADING = 'Управление autoshutdown Jupyter Server.'


class CommandHelp(click.Command):
    """Класс команд с настройкой заголовков."""

    HEADING = ''

    def format_help(self, ctx, formatter):
        """Переопределение вывода помощи."""
        help_ = JupyterServer
        help_.HEADING = self.HEADING
        help_().format_help(ctx, formatter)


class AutoShutdownCommandHelp(click.Command):
    """Класс команд autoshutdown с настройкой заголовков."""

    HEADING = ''

    def format_help(self, ctx, formatter):
        """Переопределение вывода помощи."""
        help_ = JupyterServerAutoshutdownHelp
        help_.HEADING = self.HEADING
        help_().format_help(ctx, formatter)


class ListHelp(CommandHelp):
    """Класс помощи при работе со списком Jupyter Server."""

    HEADING = 'Отображение списка Jupyter Server.'


class GetHelp(CommandHelp):
    """Класс помощи для команды получения Jupyter Server по UUID."""

    HEADING = 'Отображение Jupyter Server по UUID.'


class ConfigHelp(CommandHelp):
    """Класс помощи для получения конфигурации Jupyter Service."""

    HEADING = 'Отображение информации о доступных регионах, инстанс типах и образах для Jupyter Server.'


class CreateHelp(CommandHelp):
    """Класс помощи для создания Jupyter Server."""

    HEADING = 'Создание Jupyter Server.'


class YamlHelp(CommandHelp):
    """Класс помощи для генерации примера YAML-манифеста create или resume."""

    HEADING = 'Генератор примера YAML для создания или перезапуска Jupyter Server.'


class DeleteHelp(CommandHelp):
    """Класс помощи для удаления Jupyter Server."""

    HEADING = 'Удаление Jupyter Server.'


class PauseHelp(CommandHelp):
    """Класс помощи для остановки Jupyter Server."""

    HEADING = 'Пауза Jupyter Server.'


class ModifyHelp(CommandHelp):
    """Класс помощи для изменения Jupyter Server."""

    HEADING = 'Изменение Jupyter Server.'


class ResumeHelp(CommandHelp):
    """Класс помощи для перезапуска Jupyter Server."""

    HEADING = 'Перезапуск Jupyter Server.'


class AutoShutdownHelp(JupyterServerAutoshutdownHelp):
    """Класс помощи для группы команд autoshutdown."""

    HEADING = 'Автовыключение Jupyter Server на уровне workspace.'

    def list_commands(self, ctx: click.Context) -> list[str]:
        """Подкоманды в порядке: get, set, delete."""
        order = ('get', 'set', 'delete')
        return [name for name in order if name in self.commands]


class AutoShutdownGetHelp(AutoShutdownCommandHelp):
    """Класс помощи для просмотра правил автовыключения (workspace)."""

    HEADING = 'Просмотр правил автовыключения Jupyter Server на уровне воркспейса.'


class AutoShutdownSetHelp(AutoShutdownCommandHelp):
    """Класс помощи для создания и обновления правил автовыключения."""

    HEADING = 'Создание или обновление правил автовыключения Jupyter Server на уровне воркспейса.'


class AutoShutdownDeleteHelp(AutoShutdownCommandHelp):
    """Класс помощи для удаления правил автовыключения (workspace)."""

    HEADING = 'Удаление правил автовыключения Jupyter Server на уровне воркспейса.'
