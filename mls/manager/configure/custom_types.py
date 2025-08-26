"""Модуль custom_types содержит определения пользовательских типов данных.

Эти типы данных кастомизированны в строчное представление для вывода в CLI.
"""
import click


class CustomGroupedOption(click.Option):
    """Класс очередности отображения."""
    GROUP: str = ''
    GROUP_INDEX = 0
    INTEND = 0

    def __init__(self, *args, index=0, **kwargs):
        """Метод включения сортировки внутри класса."""
        super().__init__(*args, **kwargs)
        self.group = self.GROUP
        self.group_index = self.GROUP_INDEX
        self.index = index
        self.intend = self.INTEND


class ConfigureAdditionalOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции дополнительные'
    GROUP_INDEX = 1
