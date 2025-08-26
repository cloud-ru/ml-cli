"""Тесты типов приложения cli."""
import click
import pytest

from mls.utils.common_types import Path
from mls.utils.common_types import PositiveIntWithZeroView
from mls.utils.common_types import RussianChoice


def test_types():
    """Тесты типов."""
    assert str(Path(exists=True)) == 'string'
    assert str(RussianChoice(['поработать до полуночи', 'пойти спать']).options) == (
        'Допустимые варианты: поработать до полуночи, пойти спать'
    )
    assert str(PositiveIntWithZeroView()) == 'int'


def test_positive_convector_alphabet():
    """Тест конвертации алфавита."""
    instance = PositiveIntWithZeroView()
    with pytest.raises(click.BadParameter) as err:
        instance('abc')

    assert err.value.args == ('abc не является допустимым целым числом',)


def test_positive_convector_negative():
    """Тест конвертации отрицательных чисел."""
    instance = PositiveIntWithZeroView()
    with pytest.raises(click.BadParameter) as err:
        instance(-1)
    assert err.value.args == ('-1 не является положительным числом или нулем',)


def test_positive_convector_float():
    """Тест конвертации float int."""
    instance = PositiveIntWithZeroView()
    assert instance(1.0) == 1
    assert instance(0.0) == 0
    assert instance(1.1) == 1
