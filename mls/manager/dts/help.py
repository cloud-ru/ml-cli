"""Модуль help предоставляет функции для отображения справки в cli."""
import click

from mls.utils.fomatter import CommonGroupFormatter


class CommandHelp(click.Command):
    """Класс команд с настройкой заголовков."""

    HEADING = ''

    def format_help(self, ctx, formatter):
        """Переопределение вывода помощи."""
        help_ = ConnectorHelp
        help_.HEADING = self.HEADING
        help_().format_help(ctx, formatter)


class ConnectorHelp(CommonGroupFormatter):
    """Класс помощи для группы команд коннекторов."""

    HEADING = 'Управление коннекторами.'


class TransferHelp(CommonGroupFormatter):
    """Класс помощи для группы команд правил переноса."""

    HEADING = 'Управление правилами переноса.'


class ConnectorListHelp(CommandHelp):
    """Класс помощи для получения списка коннекторов."""

    HEADING = 'Управление коннекторами.'


class ConnectorCreateHelp(CommandHelp):
    """Класс помощи для создания коннектора."""

    HEADING = 'Управление коннекторами.'


class ConnectorSourcesHelp(CommandHelp):
    """Класс помощи для получения схем коннектора."""

    HEADING = 'Управление коннекторами.'


class ConnectorUpdateHelp(CommandHelp):
    """Класс помощи для обновления коннектора."""

    HEADING = 'Управление коннекторами.'


class ConnectorActivateHelp(CommandHelp):
    """Класс помощи для активации коннектора."""

    HEADING = 'Управление коннекторами.'


class ConnectorDeactivateHelp(CommandHelp):
    """Класс помощи для деактивации коннектора."""

    HEADING = 'Управление коннекторами.'


class ConnectorDeleteHelp(CommandHelp):
    """Класс помощи для удаления коннектора."""

    HEADING = 'Управление коннекторами.'


class TransferCommandHelp(click.Command):
    """Класс команд с настройкой заголовков."""

    HEADING = ''

    def format_help(self, ctx, formatter):
        """Переопределение вывода помощи."""
        help_ = TransferHelp
        help_.HEADING = self.HEADING
        help_().format_help(ctx, formatter)


class TransferCreateHelp(TransferCommandHelp):
    """Класс помощи для создания правила переноса."""

    HEADING = 'Управление правилами переноса.'


class TransferListHelp(TransferCommandHelp):
    """Класс помощи для получения истории запусков правил переноса."""

    HEADING = 'Управление правилами переноса.'


class TransferRulesHelp(TransferCommandHelp):
    """Класс помощи для создания правила переноса."""

    HEADING = 'Управление правилами переноса.'


class TransferDeleteHelp(TransferCommandHelp):
    """Удаление правила переноса."""

    HEADING = 'Управление правилами переноса.'


class TransferUpdateHelp(TransferCommandHelp):
    """Обновление правила переноса."""

    HEADING = 'Управление правилами переноса.'


class TransferStopHelp(TransferCommandHelp):
    """Остановка переноса (отмена)."""

    HEADING = 'Управление правилами переноса.'


class TransferActivateHelp(TransferCommandHelp):
    """Включение периодического переноса."""

    HEADING = 'Управление правилами переноса.'


class TransferDeactivateHelp(TransferCommandHelp):
    """Отключение периодического переноса."""

    HEADING = 'Управление правилами переноса.'


class TransferLogsHelp(TransferCommandHelp):
    """Просмотр событий по переносу."""

    HEADING = 'Управление правилами переноса.'


class TransferHistoryHelp(TransferCommandHelp):
    """Просмотр истории запусков правил(а) переноса."""

    HEADING = 'Управление правилами переноса.'
