"""Unit-тесты общих утилит парсинга JSON для CLI-менеджеров."""
import pytest

from mls.manager.notebook_service.cli import parse_optional_json_array
from mls.manager.notebook_service.cli import parse_optional_json_object


class TestParseOptionalJsonArray:
    """Тесты `parse_optional_json_array`."""

    def test_none_returns_none(self):
        """None даёт None."""
        assert parse_optional_json_array(None) is None

    def test_empty_string_returns_none(self):
        """Пустая строка даёт None."""
        assert parse_optional_json_array('') is None

    def test_valid_array(self):
        """Валидный JSON-массив возвращается как список."""
        assert parse_optional_json_array('[]') == []
        assert parse_optional_json_array('[1, "a", {}]') == [1, 'a', {}]

    def test_invalid_json_raises(self):
        """Невалидный JSON даёт ValueError с пояснением."""
        with pytest.raises(ValueError, match='Невалидный JSON'):
            parse_optional_json_array('{')

    def test_object_not_array_raises(self):
        """JSON-объект не считается массивом."""
        with pytest.raises(ValueError, match='Ожидался JSON-массив'):
            parse_optional_json_array('{}')

    def test_string_primitive_not_array_raises(self):
        """Строка в кавычках — не массив."""
        with pytest.raises(ValueError, match='Ожидался JSON-массив'):
            parse_optional_json_array('"only-string"')

    def test_number_primitive_not_array_raises(self):
        """Число — не массив."""
        with pytest.raises(ValueError, match='Ожидался JSON-массив'):
            parse_optional_json_array('42')

    def test_bool_primitive_not_array_raises(self):
        """Литерал true — не массив."""
        with pytest.raises(ValueError, match='Ожидался JSON-массив'):
            parse_optional_json_array('true')


class TestParseOptionalJsonObject:
    """Тесты `parse_optional_json_object`."""

    def test_none_returns_none(self):
        """None даёт None."""
        assert parse_optional_json_object(None) is None

    def test_empty_string_returns_none(self):
        """Пустая строка даёт None."""
        assert parse_optional_json_object('') is None

    def test_valid_object(self):
        """Валидный JSON-объект возвращается как словарь."""
        assert parse_optional_json_object('{}') == {}
        assert parse_optional_json_object('{"k": 1, "nested": [2]}') == {'k': 1, 'nested': [2]}

    def test_invalid_json_raises(self):
        """Невалидный JSON даёт ValueError."""
        with pytest.raises(ValueError, match='Невалидный JSON'):
            parse_optional_json_object('not json')

    def test_array_not_object_raises(self):
        """Массив не считается объектом."""
        with pytest.raises(ValueError, match='Ожидался JSON-объект'):
            parse_optional_json_object('[]')

    def test_string_primitive_not_object_raises(self):
        """Строка — не объект."""
        with pytest.raises(ValueError, match='Ожидался JSON-объект'):
            parse_optional_json_object('"x"')

    def test_number_primitive_not_object_raises(self):
        """Число — не объект."""
        with pytest.raises(ValueError, match='Ожидался JSON-объект'):
            parse_optional_json_object('0')
