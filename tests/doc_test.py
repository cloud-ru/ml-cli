"""Тестовые сценарии для проверки работы форматтера."""
import shutil

import click

from mls.manager.job.help import CommandHelp
from mls.utils.cli_entrypoint_help import MLSHelp
from mls.utils.fomatter import CommonGroupFormatter
from mls.utils.fomatter import init_formater


def test_init_formatter():
    """Тест для проверки функции инициализации форматтера."""
    formatter = click.HelpFormatter()
    init_formater(formatter)
    assert len(formatter.buffer) == 0
    assert formatter.width == shutil.get_terminal_size().columns


def test_common_group_formatter(runner):
    """Тест для проверки базового кастомного форматтера."""
    @click.group(cls=CommonGroupFormatter)
    def cli():
        """Тестовая команда."""

    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Опции:' in result.output


def test_mlshelp_formatter(runner):
    """Тест для проверки специфичного для MLS форматтера."""
    @click.group(cls=MLSHelp)
    def cli():
        """Тестовая команда."""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Интерфейс командной строки MLS' in result.output


def create_test_cli():
    """Функция для создания тестовой группы команд с использованием CommonGroupFormatter."""
    @click.group(cls=CommonGroupFormatter)
    def cli():
        """Главная тестовая команда."""

    @cli.command()
    def command1():
        """Команда номер один."""

    @cli.command(hidden=True)
    def hidden_command():
        """Эта команда не должна отображаться."""

    return cli


def test_format_commands_section(runner):
    """Тест для проверки вывода списка команд."""
    cli = create_test_cli()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'command1' in result.output
    assert 'hidden_command' not in result.output
    assert 'Команда номер один' in result.output


def create_advanced_test_cli():
    """Функция для создания тестовой группы команд с подгруппой команд."""
    @click.group(cls=CommonGroupFormatter)
    def cli():
        """Главная тестовая команда."""

    @cli.command()
    def command1():
        """Команда номер один."""

    # Определение подгруппы команд внутри основной группы
    @cli.group()
    def subgroup():
        """Подгруппа команд."""
        pass

    @subgroup.command()
    def subcommand1():
        """Подкоманда номер один."""

    return cli


def test_advanced_format_commands_section(runner):
    """Тест для проверки вывода с вложенными группами команд."""
    cli = create_advanced_test_cli()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'command1' in result.output
    assert 'subgroup' in result.output
    assert 'Подгруппа команд' in result.output
    result_subgroup = runner.invoke(cli, ['subgroup', '--help'])
    assert 'subcommand1' in result_subgroup.output
    assert 'Подкоманда номер один' in result_subgroup.output


def create_command_with_options():
    """Создание тестовой команды с различными типами параметров."""
    @click.command(cls=CommonGroupFormatter)
    @click.argument('arg', type=str)
    @click.option('--option-with-help', help='Тестовая опция с описанием.')
    @click.option('--option-without-help')
    def test_command(arg, option_with_help, option_without_help):
        """Тестовая команда."""
        pass

    return test_command


def test_format_options_section(runner):
    """Тест для проверки форматирования раздела опций с соответствующими случаями."""
    cmd = create_command_with_options()
    result = runner.invoke(cmd, ['--help'])
    assert result.exit_code == 0
    assert 'arg' in result.output
    assert '--option-with-help' in result.output
    assert 'Тестовая' in result.output
    assert 'опция с описанием.' in result.output
    assert '--option-without-help' in result.output
    assert 'string' in result.output


class MyTestCommand(CommandHelp):
    """Тестовая команда."""
    HEADING = 'Тестовый заголовок'


def create_any_test_cli():
    """Функция для создания внутри группы подкоманды."""
    @click.group()
    def cli():
        """Главная тестовая команда."""
        pass

    @cli.command(cls=MyTestCommand)
    def test_command():
        """Тестовая подкоманда."""
        click.echo('Тестовый вывод')

    return cli


def test_command_help_heading(runner):
    """Тест для проверки правильности отображения заголовка в справке."""
    cli = create_any_test_cli()
    result = runner.invoke(cli, ['test-command', '--help'])
    assert result.exit_code == 0
    assert 'Тестовый заголовок' in result.output
    assert 'Тестовая подкоманда' in result.output
