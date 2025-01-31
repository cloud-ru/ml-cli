"""Группы стилей для cli консоли."""
from functools import partial

import click

# Настройка форматирования сообщений команд
message_format = partial(click.style, fg='cyan', bold=True)
success_format = partial(click.style, fg='green', bold=True)
error_format = partial(click.style, fg='red', bold=True)

# Настройка форматирования сообщений help
text_format = partial(click.style, bold=False)
highlight_format = partial(click.style, fg='bright_white', bold=True)
