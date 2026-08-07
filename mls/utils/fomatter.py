"""Модуль формат.

Определяет поведение отображения справочной информации всего проекта.
"""
import shutil

import click
from click import Argument

from .style import highlight_format
from .style import text_format


class ArgumentWithHelpLine(click.Argument):
    """Аргумент с подписью в разделе «Аргументы» (CommonGroupFormatter)."""

    def __init__(self, *param_decls, argument_help: str = '', **attrs):
        """Инициализирует аргумент и сохраняет строку подписи для форматтера справки.

        Args:
            *param_decls: Декларации имени аргумента для ``click.Argument``.
            argument_help: Текст, выводимый в разделе «Аргументы» рядом с именем параметра.
            **attrs: Прочие аргументы конструктора ``click.Argument``.
        """
        self.argument_help = argument_help
        super().__init__(*param_decls, **attrs)


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
        for _ in range(0, count):
            formatter.indent()

    @staticmethod
    def dedent(count, formatter: click.HelpFormatter):
        """Убирает уровни отступа в форматтере.

        :param count: Количество уровней возврата.
        :param formatter: Форматтер, в котором убираются уровни отступа.
        """
        for _ in range(0, count):
            formatter.dedent()

    def format_usage(self, ctx, formatter: click.HelpFormatter):
        """Форматирует строку использования команды.

        :param ctx: Контекст выполнения команды.
        :param formatter: Форматтер справочной информации.
        """
        prefix = text_format(
            formatter.current_indent *
            ' ' + 'Синтаксис: ',
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

    @staticmethod
    def sort_custom_structure(data):
        """Метод сортировки по ключу для групп и подгрупп."""
        sorted_groups = sorted(data.keys(), key=lambda k: data[k]['sort_key'])

        # Сортируем элементы внутри групп
        for group_name in sorted_groups:
            group = data[group_name]
            group['items'].sort(key=lambda item: item['sort_key'])

        # Возвращаем новый отсортированный словарь
        return {group_name: data[group_name] for group_name in sorted_groups}

    def format_options_section(self, ctx: click.Context, formatter: click.HelpFormatter):
        """Форматирует раздел опций команды."""
        opts = ctx.command.params or self.get_params(ctx)
        arguments, options = self.separate_arguments_options(opts)
        self.extract_argument(arguments, formatter)
        groups: dict = {}
        for param in options:
            group_str = getattr(param, 'group', 'Опции')
            group_index = getattr(param, 'group_index', -9999)
            index = getattr(param, 'index', -9999)
            intend = getattr(param, 'intend', 0)
            groups[group_str] = groups.get(group_str, {'sort_key': group_index, 'items': [], 'intend': intend})
            groups[group_str]['items'].append({'sort_key': index, 'value': param})

        if options:
            for param_name, ordered_param in self.sort_custom_structure(groups).items():
                intend = ordered_param['intend']
                items = ordered_param['items']
                self.indent(intend, formatter)
                with formatter.section(text_format(param_name)):
                    for item in items:
                        param = item['value']
                        if self.is_help_option(param):
                            formatter.write_text(text_format(f'--{param.name}'))
                        else:
                            help_option = getattr(param, 'help', None) or '-'
                            secondary_opts = getattr(param, 'secondary_opts', None) or []
                            if secondary_opts:
                                help_option = f'{help_option}. Обратные флаги: {" ".join(secondary_opts)}'
                            if not getattr(param, 'hidden', False):
                                formatter.write_text(
                                    highlight_format(
                                        f'{" ".join(param.opts):<25}',
                                    ) + text_format(f' [{str(param.type).lower():<10}]  {help_option}'),
                                )
                    self.dedent(intend, formatter)

    @staticmethod
    def extract_argument(arguments, formatter):
        """Метод печати справки по аргументам."""
        if arguments:
            with formatter.section(text_format('Аргументы')):
                for param in arguments:
                    arg_help = getattr(param, 'argument_help', None) or getattr(param, 'help', None) or ''
                    line = highlight_format(f'{param.name}')
                    if arg_help:
                        line += text_format(f'  {arg_help}')
                    formatter.write_text(line)

    @staticmethod
    def is_help_option(param):
        """Определяет встроенную Click help-option без привязки к внутренним классам Click."""
        return getattr(param, 'name', None) == 'help' and '--help' in getattr(param, 'opts', ())

    @staticmethod
    def separate_arguments_options(opts):
        """Метод разделения аргументов и опций."""
        arguments = []
        options = []
        if opts:
            for param in opts:
                if len(param.opts) and param.name.replace('_', '-', -1) == param.opts[0] or isinstance(param, Argument):
                    arguments.append(param)
                else:
                    options.append(param)
        return arguments, options

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
                        child_commands = '|'.join(cmd.list_commands(ctx))
                        text = (cmd.help or '').replace('[command]', f'[{child_commands}]')
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
        self.format_options_section(ctx, formatter)
        self.format_commands_section(ctx, formatter)

        # Получаем отформатированный текст помощи
        rendered_text = [*formatter.buffer]
        if len(rendered_text) > shutil.get_terminal_size().lines:
            click.echo_via_pager(rendered_text)
            formatter.buffer = []
        else:
            pass
