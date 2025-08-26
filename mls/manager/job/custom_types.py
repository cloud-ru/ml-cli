"""Модуль custom_types содержит определения пользовательских типов данных.

Эти типы данных кастомизированны в строчное представление для вывода в CLI.
"""
import click

from mls.manager.job.constants import cluster_keys
from mls.manager.job.constants import job_actions_in_fail
from mls.manager.job.constants import job_statuses
from mls.manager.job.constants import job_types
from mls.manager.job.constants import priority
from mls.manager.job.constants import table_sort_filter_fields
from mls.utils.common_types import PositiveIntWithZeroView
from mls.utils.common_types import RussianChoice

priority_class = RussianChoice(priority)
filter_sort_choice = RussianChoice(table_sort_filter_fields)
job_types_input = RussianChoice(job_types)
worker_input = PositiveIntWithZeroView()
cluster_key_input = RussianChoice(cluster_keys)
status_inputs = RussianChoice(job_statuses)
job_actions_in_fail_input = RussianChoice(job_actions_in_fail)


class ExternalActionView(click.ParamType):
    """Класс отображения NFS пути."""
    name = 'external_action'

    def __repr__(self):
        """Метод __repr__.

        Возвращает строку с отображением пути.
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return 'list_optional_choice'


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


class ProfileOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции профиля'
    GROUP_INDEX = 11


class JobRequiredOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Минимальный набор опций для запуска задачи:'
    GROUP_INDEX = -9999 - 1


class JobRecommenderOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Манифест параметров запуска задачи:'
    GROUP_INDEX = -9999 - 2


class JobDebugOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции отладки'
    GROUP_INDEX = 100


class JobEnvironmentOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции управления окружением:'
    GROUP_INDEX = 3


class JobResourceOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции управления ресурсами:'
    GROUP_INDEX = 4


class JobPolicyOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции управления политиками:'
    GROUP_INDEX = 5


class JobPolicyAllocationOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции управления в аллокации:'
    GROUP_INDEX = 6


class JobHealthOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции управления оповещением:'
    GROUP_INDEX = 7


class JobElasticOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции управления Pytorch Elastic:'
    GROUP_INDEX = 8


class JobPytorch2Options(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции управления Pytorch2:'
    GROUP_INDEX = 9


class FilterOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции фильтрации:'
    GROUP_INDEX = 8


class SortOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции сортировки:'
    GROUP_INDEX = 9
