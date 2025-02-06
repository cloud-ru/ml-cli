"""Модуль формат.

Определяет поведение отображения справочной информации всего проекта.
"""
import shutil

import click

from .style import highlight_format
from .style import text_format


def init_formater(formatter: click.HelpFormatter):
    """Инициализирует форматтер с настройками ширины вывода, соответствующими размеру терминала, и поменяет буфер.

    :param formatter: Экземпляр форматтера Click, который будет инициализирован.
    """
    formatter.width = shutil.get_terminal_size().columns
    formatter.buffer = []


class CommonGroupFormatter(click.Group):
    """Кастомный класс для группы команд с собственным форматированием помощи."""

    # Предварительно установленный заголовок; переопределяется в подклассах.
    HEADING = ''

    @staticmethod
    def indent(count, formatter: click.HelpFormatter):
        """Выполняет отступ в форматтере на заданное количество уровней.

        :param count: Количество уровней отступа.
        :param formatter: Форматтер, в котором выполняется отступ.
        """
        for i in range(0, count):
            formatter.indent()

    @staticmethod
    def dedent(count, formatter: click.HelpFormatter):
        """Убирает уровни отступа в форматтере.

        :param count: Количество уровней возврата.
        :param formatter: Форматтер, в котором убираются уровни отступа.
        """
        for i in range(0, count):
            formatter.dedent()

    def format_usage(self, ctx, formatter: click.HelpFormatter):
        """Форматирует строку использования команды.

        :param ctx: Контекст выполнения команды.
        :param formatter: Форматтер справочной информации.
        """
        prefix = text_format(
            formatter.current_indent *
            ' ' + 'Использование: ',
        )
        formatter.write_usage(
            text_format(ctx.command_path),
            'COMMAND [ARGS] [OPTIONS]', prefix=prefix,
        )

    def format_heading(self, formatter: click.HelpFormatter):
        """Форматирует заголовки секций справки.

        :param formatter: Форматтер справочной информации.
        """
        formatter.write_text('')
        self.indent(4, formatter)
        formatter.write_text(highlight_format(self.HEADING))

    def format_help_text(self, ctx: click.Context, formatter: click.HelpFormatter):
        """Форматирует и выводит дополнительный текст помощи.

        :param ctx: Контекст выполнения команды.
        :param formatter: Форматтер справочной информации.
        """
        help_text = ctx.command.help or ''
        if help_text:
            formatter.write_text(text_format(help_text + '\n'))
        formatter.write_text('')

    def format_options_section(self, ctx: click.Context, formatter: click.HelpFormatter):
        """Форматирует раздел опций команды."""
        opts = ctx.command.params or self.get_params(ctx)
        arguments = []
        options = []
        if opts:
            for param in opts:
                if len(param.opts) and param.name == param.opts[0]:
                    arguments.append(param)
                else:
                    options.append(param)

        if arguments:
            with formatter.section(text_format('Аргументы')):
                self.indent(2, formatter)
                for param in arguments:
                    formatter.write_text(
                        highlight_format(f'{param.name.upper()}'),
                    )
                self.dedent(2, formatter)

        if options:
            with formatter.section(text_format('Опции')):
                self.indent(2, formatter)
                for param in options:
                    if isinstance(param, click.decorators.HelpOption):
                        formatter.write_text(text_format(f'--{param.name}'))
                    else:
                        help_option = getattr(param, 'help', None) or '-'
                        formatter.write_text(
                            highlight_format(
                                f'--{param.name:<15}',
                            ) + text_format(f' ::[{str(param.type):>10}]  {help_option}'),
                        )
                self.dedent(2, formatter)

    def format_commands_section(self, ctx: click.Context, formatter: click.HelpFormatter):
        """Форматирует раздел доступных в группе команд."""
        commands = self.list_commands(ctx)
        if commands:
            with formatter.section(text_format('Команды')):
                self.indent(2, formatter)
                for command in commands:
                    cmd = self.get_command(ctx, command)
                    if cmd is None or cmd.hidden:
                        continue
                    formatter.write_text(highlight_format(command))
                    if isinstance(cmd, click.Group):
                        commands = '|'.join(cmd.list_commands(ctx))
                        text = cmd.help.replace('[command]', f'[{commands}]')
                        formatter.write_text(text_format(f'{text}'))
                        formatter.write_text('')
                    else:
                        formatter.write_text(text_format(cmd.help) or '')
                self.dedent(2, formatter)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter):
        """Переопределяет метод форматирования вывода справки по умолчанию.

        :param ctx: Контекст выполнения команды.
        :param formatter: Форматтер справочной информации.
        """
        init_formater(formatter)
        self.format_heading(formatter)
        self.format_help_text(ctx, formatter)
        self.format_usage(ctx, formatter)
        self.format_options_section(ctx, formatter)
        self.format_commands_section(ctx, formatter)

        # Получаем отформатированный текст помощи
        rendered_text = [*formatter.buffer]
        if len(rendered_text) > shutil.get_terminal_size().lines:
            click.echo_via_pager(rendered_text)
        else:
            pass
