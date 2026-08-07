"""Тестовые сценарии для проверки работы форматтера."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import click
import pytest

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


def test_format_options_section_includes_secondary_bool_options(runner):
    """Кастомный formatter показывает обе стороны boolean-флага."""
    @click.command(cls=CommonGroupFormatter)
    @click.option('--timer-enabled/--timer-disabled', default=True, help='Таймер')
    def cmd(timer_enabled):
        """Тестовая команда."""
        pass

    result = runner.invoke(cmd, ['--help'])

    assert result.exit_code == 0
    assert '--timer-enabled' in result.output
    assert '--timer-disabled' in result.output


def render_cli_doc(tmp_path: Path, command: str) -> str:
    """Рендерит rst-документацию из help-output локального CLI."""
    output_path = tmp_path / 'command.rst'
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    env['COLUMNS'] = '300'
    env['LINES'] = '300'
    subprocess.run(
        [
            sys.executable,
            'docs/script.py',
            'docs/template.rst',
            f'{sys.executable} ./mls/cli.py {command} --help',
            str(output_path),
        ],
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )
    return output_path.read_text(encoding='utf-8')


@pytest.mark.parametrize(
    'command, expected_options',
    [
        ('js create', ['--namespace', '--name', '--image-name', '--instance-type']),
        ('js list', ['--notebook-type', '--status', '--access_mode']),
        ('js modify', ['--shutdown-in', '--timer-disabled', '--s3-buckets-json']),
        ('js resume', ['--namespace', '--instance-type']),
        ('js autoshutdown set', ['--shutdown-in', '--timer-disabled', '--by-timer-json']),
        ('tensorboard create', ['--namespace', '--name', '--logdir', '--tensorboard-params']),
        ('tensorboard list', ['--order_by', '--status']),
        ('tensorboard modify', ['--shutdown-in', '--timer-disabled', '--s3-buckets-json']),
        ('tensorboard resume', ['--namespace', '--instance-type']),
        ('ws list', ['--customer-id']),
    ],
)
def test_generated_docs_include_service_command_options(tmp_path, command, expected_options):
    """Генерация docs из --help сохраняет параметры команд."""
    rendered = render_cli_doc(tmp_path, command)

    for option in expected_options:
        assert option in rendered


def test_generated_docs_normalize_command_whitespace(tmp_path):
    """Генерация docs схлопывает отступы многострочного примера команды."""
    rendered = render_cli_doc(tmp_path, 'js create')

    assert (
        'mls js create --namespace default --name my-js --image-name '
        'cr.ai.cloud.ru/aicloud-jupyter/jupyter-server --image-tag latest '
        '--image-type datahub --instance-type free.0gpu'
    ) in rendered


def test_generated_docs_use_single_spaces_between_option_names(tmp_path):
    """Имена опций в list-table разделяются одним пробелом."""
    rendered = render_cli_doc(tmp_path, 'js create')

    assert '   * - ``--image-name``\n' in rendered
    assert '   * - ``-c`` ``--config``\n' in rendered


class MyTestCommand(CommandHelp):
    """Тестовая команда."""
    HEADING = 'Тестовый заголовок'


def create_any_test_cli():
    """Функция для создания внутри группы подкоманды."""
    @click.group()
    def cli():
        """Главная тестовая команда."""
        pass

    @cli.command(cls=MyTestCommand, name='test-command')
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
