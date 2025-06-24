"""Script for rendering Jinja2 templates using command output.

This module provides functionality to execute shell commands, parse their output,
and use the parsed data to render Jinja2 templates.
"""
import argparse
import os
import re
import subprocess
import sys

from jinja2 import Environment


def remove_last(value):
    """Удаляет последний символ из строки."""
    return value[:-1]


def populate_eq(value):
    """Удаляет последний символ из строки."""
    return len(value) * '='


def empty():
    """Удаляет последний символ из строки."""
    return ' '


def execute_command(command):
    """Выполняет shell-команду и возвращает её вывод в виде списка строк."""
    env = os.environ.copy()
    env['COLUMNS'] = '300'  # Установите нужное количество столбцов
    env['LINES'] = '300'  # Установите нужное количество строк (опционально)
    result = subprocess.run(command, shell=True, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f'Ошибка выполнения команды: {result.stderr}', file=sys.stderr)
        sys.exit(1)
    return result.stdout.splitlines()


def parse_command_output(command_output):
    """Парсит вывод команды на секции и параметры."""
    sections = {}
    current_section = None
    pattern = r'^\s*(?P<short_opt>-\w\s+)?(?P<long_opt>--\w+(?:-\w+)*)\s*(::\s*\[\s*(?P<format>[^]]*)\s*\])?\s+(?P<description>.+)$'
    for line in command_output:
        if line.strip().endswith(':'):
            current_section = line.strip()
            sections[current_section] = []
        elif current_section and line.strip():
            match = re.match(pattern, line.strip())
            if match:
                param = match.group('short_opt') or ''
                long = match.group('long_opt')
                fmt = match.group('format') or ''
                desc = match.group('description')
                sections[current_section].append((param, long, fmt, desc))

    return sections


def main(template_filename, command, output_filename, **kwargs):
    """Основная функция рендеринга шаблона Jinja2."""
    with open(template_filename, 'r', encoding='utf-8') as file:
        template_content = file.read()

    command_output = execute_command(command)
    options = parse_command_output(command_output)

    parsed_output = {
        'line': command_output,
        'options': options,
    }

    # Создание окружения и добавление фильтра
    env = Environment()
    env.filters['remove_last'] = remove_last
    env.filters['empty'] = empty
    env.filters['populate_eq'] = populate_eq

    # Создание шаблона из содержания файла
    template = env.from_string(template_content)

    # Рендеринг шаблона
    rendered = template.render(line=parsed_output['line'], options=parsed_output['options'], **kwargs)

    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(rendered)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Render a Jinja2 template using command output.')
    parser.add_argument('template_file', help='Path to the Jinja2 template file.')
    parser.add_argument('command', help='Shell command whose output is used for the template.')
    parser.add_argument('output_file', help='Path to the output file.')
    args = parser.parse_args()

    main(
        args.template_file, args.command, args.output_file, full_command=' '.join(args.command.split()[:-1]),
        last_argument=args.command.split()[-2],
    )
