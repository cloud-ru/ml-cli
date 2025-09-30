"""Определение общих типов данных для всего проекта.

Этот модуль содержит классы, устанавливающие поведение Click Option и Click Params.

"""
import click


class Path(click.Path):
    """Класс-обертка над click.Path для кастомизации строкового представления путей."""

    def __str__(self):
        """Метод __str__.

        Возвращает строку 'OS.PATH', символизируя, что класс представляет путь в
        операционной системе. Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return 'string'


class RussianChoice(click.Choice):
    """Класс для перевода ошибок ввода на русский язык."""

    def __init__(self, choices):
        """Метод инициализирует экземпляр класса."""
        super().__init__(choices)

    def __repr__(self):
        """Метод отображает список возможных вариантов."""
        return 'choice'

    @property
    def options(self):
        """Метод отображает список допустимых вариантов разделенных запятой."""
        return 'Допустимые варианты: ' + ', '.join(f'{c}' for c in self.choices)

    def convert(self, value, param, ctx):
        """Метод заменяет наследуемый новым сообщением об ошибке."""
        try:
            return super().convert(value, param, ctx)
        except click.BadParameter:
            choices_str = ', '.join(f"'{c}'" for c in self.choices)
            self.fail(
                f"Недопустимый выбор '{value}'. Допустимые варианты: {choices_str}",
                param,
                ctx,
            )
            return None


class PositiveIntWithZeroView(click.ParamType):
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

        if int_value < 0:
            self.fail(
                f'{value} не является положительным числом или нулем', param, ctx,
            )

        return int_value

    def __str__(self):
        """Метод __str__.

        Возвращает строку 'INT GTE(0)'.
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return 'int'


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
            return dict((pair.split('=') for pair in kv_pairs))
        except Exception as e:
            self.fail(f'Ошибка при преобразовании {value} в ключ=значение. Пар: {e}')
            return None

    def __repr__(self):
        """Метод __repr__.

        Возвращает строку с отображением передачи переменных окружения или флагов.
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return 'dict'


class IntOrStrView(click.ParamType):
    """Класс преобразователь для целых значений или default."""

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
        return 'union_int_or_str'


class RangeView(click.ParamType):
    """Класс конвектор позитивных целых чисел."""

    def __init__(self, start_range: int, end_range: int):
        """Определение range начала и конца."""
        self.start_range = start_range
        self.end_range = end_range

    def convert(self, value, param, ctx):
        """Устанавливает правила валидации неотрицательных чисел."""
        try:
            int_value = int(value)
        except ValueError:
            self.fail(
                f'{value} не является допустимым целым числом', param, ctx,
            )

        if self.end_range <= int_value < self.start_range:
            self.fail(
                f'{value} задается больше в пределах [ {self.start_range + 1} .. {self.end_range} ]', param, ctx,
            )

        return int_value

    def __str__(self):
        """Метод __str__.

        Возвращает строку 'INT IN [start + 1 ... end]'
        Это упрощенное представление, не отражающее реальный
        путь или его свойства, а служащее лишь предметом кастомизации.
        """
        return 'RANGE'


out_put_format = 'json', 'text'
config_option_format_of_output = RussianChoice(out_put_format)
