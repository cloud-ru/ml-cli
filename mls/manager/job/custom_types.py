"""Модуль custom_types содержит определения пользовательских типов данных.

Эти типы данных кастомизированны в строчное представление для вывода в CLI.
"""
import click

from mls.utils.common_types import Choice

job_statuses = 'Completed', 'Completing', 'Deleted', 'Failed', 'Pending', 'Running', 'Stopped', 'Succeeded', 'Terminated'
output_formats = json, text = 'json', 'text'
priority = 'low', 'medium', 'high'  # TODO вынести в константы
table_sort_filter_fields = 'gpu_count', 'instance_type', 'job_desc', 'job_name'

priority_class = Choice(priority)
job_choices = Choice(job_statuses)
output_choice = Choice(output_formats)
filter_sort_choice = Choice(table_sort_filter_fields)
job_types = 'binary', 'horovod', 'pytorch', 'pytorch2', 'pytorch_elastic', 'spark', 'binary_exp'
cluster_keys = 'DGX2-MT', 'A100-MT', 'SR002-MT', 'SR003', 'SR004', 'SR005', 'SR006', 'SR008'  # TODO константы


class ViewRegionKeys(click.ParamType):
    """Класс для отображения ключей регионов в CLI."""

    name = 'view_region_keys'

    def __repr__(self):
        """Метод __repr__.

        Возвращает строку ключей регионов.
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return ','.join(cluster_keys)


class ViewTypeTask(click.ParamType):
    """Класс отображения справочной информации по типам задач."""
    ame = 'view_type_task'

    def __repr__(self):
        """Метод __repr__.

        Возвращает строку с отображением типов задач.
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return ', '.join(job_types)


class MaxRetryInView(click.ParamType):
    """Класс конвектор позитивных целых чисел."""
    name = 'positive_int_with_zero'

    def convert(self, value, param, ctx):
        """Устанавливает правила валидации неотрицательных чисел."""
        try:
            int_value = int(value)
        except ValueError:
            self.fail(
                f'{value} не является допустимым целым числом', param, ctx,
            )

        if 100 <= int_value < 2:
            self.fail(
                f'{value} задается больше в пределах [ 3 .. 100 ]', param, ctx,
            )

        return int_value

    def __str__(self):
        """Метод __str__.

        Возвращает строку 'INT IN [3 ... 100]'
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return 'RANGE (3 .. 100)'


class IntOrDefaultView(click.ParamType):
    """Класс преобразователь для целых значений или default."""
    name = 'int_or_default'

    def convert(self, value, param, ctx):
        """Преобразование целого числа или default."""
        try:
            return int(value)
        except ValueError:
            return str(value)

    def __str__(self):
        """Метод __str__.

        Возвращает строку 'INT || default'.
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return 'INT || \'default\''


class NFSPathView(click.ParamType):
    """Класс отображения NFS пути."""
    name = 'NFSPath'

    def __repr__(self):
        """Метод __repr__.

        Возвращает строку с отображением пути.
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return 'OS.PATH(/home/jovyan/...)'


class InternalActionView(click.ParamType):
    """Класс отображения NFS пути."""
    name = 'internal_action'

    def __repr__(self):
        """Метод __repr__.

        Возвращает строку с отображением пути.
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return 'delete,restart'


class ExternalActionView(click.ParamType):
    """Класс отображения NFS пути."""
    name = 'external_action'

    def __repr__(self):
        """Метод __repr__.

        Возвращает строку с отображением пути.
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return '["notify"]'


class ExecuteScriptView(click.ParamType):
    """Класс отображения исполняемых файлов или скриптов пути."""
    name = 'NFSPath'

    def __repr__(self):
        """Метод __repr__.

        Возвращает строку с отображением пути.
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return 'ls -lah || OS.PATH(/home/jovyan/test_script.py)'


class DictView(click.ParamType):
    """Класс отображения написания переменных и флагов."""
    name = 'dict_view'

    def __init__(self, name):
        """Включение в инициализацию параметра имени параметра."""
        self.name = name

    def convert(self, value, param, ctx):
        """Метод преобразования строки ключей-значений в словарь."""
        try:
            kv_pairs = value.split(',')
            return {k: v for k, v in (pair.split('=') for pair in kv_pairs)}
        except Exception as e:
            self.fail(f'Ошибка при преобразовании {value} в ключ=значение. Пар: {e}')

    def __repr__(self):
        """Метод __repr__.

        Возвращает строку с отображением передачи переменных окружения или флагов.
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return f'{self.name} key1=value1,key2=value2'


int_or_default = IntOrDefaultView()


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
    GROUP: str = 'Дополнительные опции управления окружением:'
    GROUP_INDEX = 3


class JobResourceOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Дополнительные опции управления ресурсами:'
    GROUP_INDEX = 4


class JobPolicyOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Дополнительные опции управления политиками:'
    GROUP_INDEX = 5


class JobPolicyAllocationOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Дополнительные опции управления в аллокации:'
    GROUP_INDEX = 6


class JobHealthOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Дополнительные опции управления оповещением:'
    GROUP_INDEX = 7


class JobElasticOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Дополнительные опции управления Pytorch Elastic:'
    GROUP_INDEX = 8


class JobPytorch2Options(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Дополнительные опции управления Pytorch2:'
    GROUP_INDEX = 9


class JobSparkOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Дополнительные опции управления Spark:'
    GROUP_INDEX = 10


class FilterOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции фильтрации:'
    GROUP_INDEX = 8


class SortOptions(CustomGroupedOption):
    """Класс очередности отображения."""
    GROUP: str = 'Опции сортировки:'
    GROUP_INDEX = 9
