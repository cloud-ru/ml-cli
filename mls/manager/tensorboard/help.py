"""Модуль помощи для CLI команд TensorBoards MLS."""
import click

from mls.utils.fomatter import CommonGroupFormatter


class TensorboardHelp(CommonGroupFormatter):
    """Класс помощи для группы команд TensorBoard."""

    HEADING = 'Управление TensorBoard.'


class CommandHelp(click.Command):
    """Класс команд с настройкой заголовков."""

    HEADING = ''

    def format_help(self, ctx, formatter):
        """Переопределение вывода помощи."""
        help_ = TensorboardHelp
        help_.HEADING = self.HEADING
        help_().format_help(ctx, formatter)


class ListHelp(CommandHelp):
    """Класс помощи при работе со списком TensorBoards."""

    HEADING = 'Отображение списка TensorBoard.'


class GetHelp(CommandHelp):
    """Класс помощи для команды получения TensorBoard по UUID."""

    HEADING = 'Отображение TensorBoard по UUID.'


class ConfigHelp(CommandHelp):
    """Класс помощи для получения конфигурации TensorBoard Service."""

    HEADING = 'Отображение информации о доступных регионах, инстанс типах и образах для TensorBoard.'


class CreateHelp(CommandHelp):
    """Класс помощи для создания TensorBoard."""

    HEADING = 'Создание TensorBoard.'


class YamlHelp(CommandHelp):
    """Класс помощи для генерации примера YAML-манифеста create или resume."""

    HEADING = 'Генератор примера YAML для создания или возобновления TensorBoard.'


class ResumeHelp(CommandHelp):
    """Класс помощи для возобновления TensorBoard."""

    HEADING = 'Перезапуск TensorBoard.'


class PauseHelp(CommandHelp):
    """Класс помощи для приостановки TensorBoard."""

    HEADING = 'Пауза TensorBoard.'


class DeleteHelp(CommandHelp):
    """Класс помощи для удаления TensorBoard."""

    HEADING = 'Удаление TensorBoard.'


class ModifyHelp(CommandHelp):
    """Класс помощи для изменения TensorBoard."""

    HEADING = 'Изменение TensorBoard.'
