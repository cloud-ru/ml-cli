"""Тестовые сценарии различных функций."""
import json
from unittest.mock import Mock
from unittest.mock import patch
from uuid import uuid4

import click.exceptions
import pytest

from mls.manager.dts.custom_types import ALL_CONNECTOR_TYPES
from mls.manager.dts.custom_types import Connector
from mls.manager.dts.custom_types import CronViewModel
from mls.manager.dts.custom_types import S3Type
from mls.manager.dts.custom_types import SQLType
from mls.manager.dts.custom_types import STRATEGY
from mls.manager.dts.custom_types import TARGET_CONNECTOR_TYPES
from mls.manager.dts.custom_types import TRANSFER_FIELD_NAMES
from mls.manager.dts.decorators import validate_positive
from mls.manager.dts.table import display_transfers
from mls.manager.dts.table import process_cron
from mls.manager.dts.table import process_transfer_table_content
from mls.manager.dts.utils import collect_connector_params
from mls.manager.dts.utils import paginate
from mls.manager.dts.utils import process_json
from mls.manager.dts.utils import RussianChoice
from mls.manager.dts.utils import validate_connector_exists
from mls.manager.dts.utils import validate_ints


class TestValidateConnector:
    """Класс тестов на валидацию коннектора."""

    def test_validate_connector_exists_success(self):
        """Успешная проверка существующего коннектора."""
        mock_api = Mock()
        connector_id = str(uuid4())
        typ = 's3custom'

        mock_api.conn_list.return_value = json.dumps([{'connector_id': connector_id}])

        result = validate_connector_exists(mock_api, connector_id, typ)

        assert result is True
        mock_api.conn_list.assert_called_once_with(
            connector_ids=[connector_id], typ=typ,
        )

    def test_validate_connector_exists_not_found(self):
        """Коннектор не найден."""
        mock_api = Mock()
        mock_api.conn_list.return_value = json.dumps([])

        result = validate_connector_exists(mock_api, uuid4(), 'mssql')

        assert result is False

    def test_validate_connector_exists_wrong_id(self):
        """Возвращается коннектор с другим ID."""
        typ = 'postgresql'

        mock_api = Mock()
        mock_api.conn_list.return_value = json.dumps([{'connector_id': str(uuid4())}])

        result = validate_connector_exists(mock_api, uuid4(), typ)

        assert result is False

    def test_validate_connector_exists_api_error(self):
        """Тест обработки ошибки API."""
        mock_api = Mock()
        mock_api.conn_list.side_effect = Exception('API error')

        connector_id = uuid4()

        with pytest.raises(click.exceptions.UsageError) as excinfo:
            validate_connector_exists(mock_api, connector_id, 'mysql')

        assert (
            f'Не удалось проверить доступность коннектора с ID: {connector_id}'
            in str(excinfo.value)
        )

    def test_validate_connector_exists_multiple_connectors(self):
        """Возвращается несколько коннекторов."""
        conn_id_1 = str(uuid4())
        conn_id_2 = str(uuid4())
        mock_api = Mock()
        mock_api.conn_list.return_value = json.dumps(
            [{'connector_id': conn_id_1}, {'connector_id': conn_id_2}],
        )

        result = validate_connector_exists(mock_api, conn_id_1, 'mysql')

        assert result is False

    def test_validate_connector_exists_invalid_response(self):
        """Некорректный ответ от API."""
        mock_api = Mock()
        mock_api.conn_list.return_value = json.dumps('invalid_response')

        result = validate_connector_exists(mock_api, uuid4(), 'mysql')

        assert result is False


class TestChoice:
    """Класс тестов на обработку ошибки при некорректном значении choice."""

    def test_russian_choice_init(self):
        """Инициализация с допустимыми вариантами."""
        rc = RussianChoice(ALL_CONNECTOR_TYPES)
        assert rc.choices == ALL_CONNECTOR_TYPES

    def test_russian_choice_repr(self):
        """Тест строкового представления."""
        choices = STRATEGY
        rc = RussianChoice(choices)
        assert repr(rc) == ', '.join(STRATEGY)

    def test_convert_valid_choice(self):
        """Тест конвертации допустимого значения."""
        choices = ['mysql', 'postgresql', 's3custom']
        rc = RussianChoice(choices)
        result = rc.convert('s3custom', None, None)
        assert result == 's3custom'

    def test_convert_invalid_choice(self):
        """Тест конвертации недопустимого значения."""
        choices = ['mssql', 's3custom']
        rc = RussianChoice(choices)

        with pytest.raises(click.BadParameter) as excinfo:
            rc.convert('invalid_connector_type', None, None)

        assert "Недопустимый выбор 'invalid_connector_type'" in str(excinfo.value)
        assert "Допустимые варианты: 'mssql', 's3custom'" in str(excinfo.value)

    def test_convert_case_sensitive(self):
        """Тест чувствительности к регистру."""
        choices = ['MySQL', 'PostgreSQL']
        rc = RussianChoice(choices)

        result = rc.convert('MySQL', None, None)
        assert result == 'MySQL'

        with pytest.raises(click.BadParameter):
            rc.convert('mysql', None, None)

    def test_empty_choices(self):
        """Тест с пустым списком вариантов."""
        rc = RussianChoice([])
        with pytest.raises(click.BadParameter) as excinfo:
            rc.convert('any_value', None, None)
        assert "Недопустимый выбор 'any_value'" in str(excinfo.value)
        assert 'Допустимые варианты: ' in str(excinfo.value)

    def test_convert_with_param_and_ctx(self):
        """Тест с передачей param и ctx."""
        choices = TARGET_CONNECTOR_TYPES
        rc = RussianChoice(choices)
        param = click.Option(['--connector_type'])
        ctx = click.Context(click.Command('create'))

        result = rc.convert('s3custom', param, ctx)
        assert result == 's3custom'

        with pytest.raises(click.BadParameter):
            rc.convert('invalid_option', param, ctx)

    def test_error_message_format(self):
        """Тест формата сообщения об ошибке."""
        choices = ['json', 'text']
        rc = RussianChoice(choices)

        try:
            rc.convert('html', None, None)
        except click.BadParameter as e:
            assert "Недопустимый выбор 'html'" in repr(e)
            assert "'json', 'text'" in str(e)
        else:
            pytest.fail('Ожидалось исключение BadParameter')


@pytest.fixture
def default_now():
    """Имитация дефолтного значения datetime.datetime.now()."""
    return '2025-05-22T12:55:58.761660'


@pytest.fixture
def default_cron(default_now):
    """Имитация дефолтного значения крона."""
    return CronViewModel(
        start_at=default_now, time=None, weekdays=None, monthdays=None, period=None,
    )


class TestCronView:
    """Класс тестов обработки крон значений."""

    TIME = '12:55'

    def test_process_cron_empty_start_at(self):
        """Если start_at пустой, возвращает 'Неизвестно'."""
        cron = CronViewModel(start_at='')
        assert process_cron(cron) == 'Неизвестно'

    def test_process_cron_period(self, default_cron):
        """Проверка периодического выполнения (каждые N часов)."""
        cron = default_cron
        cron.period = 2
        assert process_cron(cron) == 'Кажд. 2ч'

    def test_process_cron_daily_time(self, default_cron):
        """Проверка ежедневного выполнения в указанное время."""
        cron = default_cron
        cron.time = self.TIME
        assert process_cron(cron) == f'Кажд. день в {cron.time}'

    def test_process_cron_weekly_time(self, default_cron):
        """Проверка еженедельного выполнения (по дням недели)."""
        cron = default_cron
        cron.time = self.TIME
        cron.weekdays = [2]
        assert process_cron(cron) == f'Кажд. Вт в {cron.time}'

    def test_process_cron_monthly_time(self, default_cron):
        """Проверка ежемесячного выполнения (по числам месяца)."""
        cron = default_cron
        cron.time = self.TIME
        cron.monthdays = [15]
        assert process_cron(cron) == f'Кажд. месяц 15 числа в {cron.time}'

    def test_process_cron_one_time(self, default_cron):
        """Проверка однократного выполнения (если нет period/time)."""
        cron = default_cron
        assert process_cron(cron) == 'Один раз'

    def test_process_cron_invalid_weekdays(self, default_cron):
        """Проверка обработки некорректных дней недели (если days не настроен)."""
        cron = default_cron
        cron.time = self.TIME
        cron.weekdays = []
        assert process_cron(cron) == f'Кажд. день в {cron.time}'


@pytest.fixture
def sample_data():
    """Имитация списка коннекторов."""
    return [{'connector_id': i, 'name': f'name_{i}'} for i in range(1, 21)]


class TestPaginate:
    """Класс тестов на функцию пагинации."""

    def test_paginate_success(self, sample_data):
        """Проверка успешной пагинации."""
        with patch('click.echo') as mock_echo:
            paginate(data=sample_data, page=2, per_page=5)
            expected_output = json.dumps(
                sample_data[5:10], indent=4, ensure_ascii=False,
            )
            mock_echo.assert_called_once()
            assert expected_output in mock_echo.call_args[0][0]

    def test_paginate_last_page(self, sample_data):
        """Проверка пагинации последней страницы."""
        with patch('click.echo') as mock_echo:
            paginate(data=sample_data, page=4, per_page=6)
            expected_output = json.dumps(
                sample_data[18:20], indent=4, ensure_ascii=False,
            )
            mock_echo.assert_called_once()
            assert expected_output in mock_echo.call_args[0][0]

    def test_paginate_empty_data(self):
        """Проверка пагинации пустых данных."""
        with patch('click.echo') as mock_echo:
            paginate(data=[], page=1, per_page=10)
            mock_echo.assert_called_once()
            assert '[]' in mock_echo.call_args[0][0]

    def test_paginate_page_out_of_range(self, sample_data):
        """Проверка пагинации при выходе за отведенный диапазон."""
        with patch('click.echo') as mock_echo:
            paginate(data=sample_data, page=999, per_page=10)
            mock_echo.assert_called_once()
            assert '[]' in mock_echo.call_args[0][0]

    def test_paginate_invalid_data(self):
        """Проверка пагинации при ошибке."""
        with pytest.raises(click.ClickException):
            paginate(data=6, page=1, per_page=10)

    def test_paginate_zero_per_page(self, sample_data):
        """Проверка пагинации с 0 элементов на странице."""
        with patch('click.echo') as mock_echo:
            paginate(data=sample_data, page=1, per_page=0)
            mock_echo.assert_called_once()
            assert '[]' in mock_echo.call_args[0][0]


@pytest.fixture
def s3_connector_type():
    """Имитация типа коннектора."""
    return 's3custom'


@pytest.fixture
def sql_connector_type():
    """Имитация типа коннектора."""
    return 'postgresql'


class TestParamsCollector:
    """Класс тестов проверки сбора параметров коннектора."""

    def test_collect_s3_connector_params(self, s3_connector_type):
        """Проверка сбора параметров для S3 коннектора."""
        with patch('click.prompt') as mock_prompt:
            mock_prompt.side_effect = [
                'test_endpoint',
                'test_bucket',
                'test_access_key',
                'test_secret_key',
                'test_connector_name',
            ]

            result = collect_connector_params(s3_connector_type)

            mock_prompt.assert_any_call('Endpoint')
            mock_prompt.assert_any_call('S3 Bucket')
            mock_prompt.assert_any_call('S3 Access Key', hide_input=True)
            mock_prompt.assert_any_call('S3 Secret Key', hide_input=True)
            mock_prompt.assert_any_call('Имя коннектора')

            assert isinstance(result, Connector)
            assert result.name == 'test_connector_name'
            assert isinstance(result.parameters, S3Type)
            assert result.parameters.endpoint == 'test_endpoint'
            assert result.parameters.bucket == 'test_bucket'

    def test_collect_sql_connector_params(self, sql_connector_type):
        """Проверка сбора парамтеов для SQL коннектора."""
        with patch('click.prompt') as mock_prompt:
            mock_prompt.side_effect = [
                'test_user',
                'test_password',
                'test_db',
                'test_host',
                5432,
                'test_connector_name',
            ]

            result = collect_connector_params(sql_connector_type)

            mock_prompt.assert_any_call('user')
            mock_prompt.assert_any_call('password', hide_input=True)
            mock_prompt.assert_any_call('database')
            mock_prompt.assert_any_call('host')

            assert isinstance(result, Connector)
            assert result.name == 'test_connector_name'
            assert isinstance(result.parameters, SQLType)
            assert result.parameters.user == 'test_user'
            assert result.parameters.port == 5432


class TestProcessData:
    """Класс тестов на функцию обработки JSON данных."""

    TEST_DATA = json.dumps([{'connector_id': i} for i in range(1, 21)])

    def test_process_data_json_with_pagination(self, mock_api_dts):
        """Обработка JSON при переданных параметрах пагинации."""
        with (
            patch('click.echo') as mock_echo,
            patch('mls.manager.dts.utils.paginate') as mock_paginate,
        ):
            mock_paginate.return_value = 'paginated_data'

            process_json(data=self.TEST_DATA, page_number=2, page_size=5)

            mock_paginate.assert_called_once()
            assert mock_paginate.call_args[1]['page'] == 2
            assert mock_paginate.call_args[1]['per_page'] == 5

            mock_echo.assert_called_once_with('paginated_data')

    @pytest.mark.parametrize('page_number, page_size', [(1, 10), (2, 10)])
    def test_process_data_json_without_pagination(self, page_number, page_size):
        """Обработка JSON при не переданных параметрах пагинации."""
        with (
            patch('click.echo') as mock_echo,
            patch('mls.utils.style.success_format') as mock_format,
        ):
            mock_format.return_value = 'formatted_data'
            process_json(
                data=self.TEST_DATA, page_number=page_number, page_size=page_size,
            )
            mock_echo.assert_called()

    def test_process_data_invalid_json(self):
        """Невалидный JSON."""
        invalid_json = '{invalid_json}'

        with patch('click.echo') as mock_echo:
            with pytest.raises(json.JSONDecodeError):
                process_json(data=invalid_json, page_number=1, page_size=10)

            mock_echo.assert_not_called()

    def test_process_data_empty_data(self):
        """Обработка пустых данных."""
        with (
            patch('click.echo') as mock_echo,
            patch('mls.utils.style.success_format') as mock_format,
            pytest.raises(json.decoder.JSONDecodeError),
        ):
            mock_format.return_value = 'formatted_empty'

            process_json(data='', page_number=1, page_size=1)

            mock_format.assert_called_once_with('')
            mock_echo.assert_called_once_with('formatted_empty')


class TestValidatePositive:
    """Класс тестов валидации позитивных значений."""

    PARAM = 'test_param'

    @pytest.mark.parametrize('param, val', [('--page_size', -99), ('--page_number', 1)])
    def test_validate_positive(self, param, val):
        """Проверка валидации page_size, page_number."""
        if val < 0:
            with pytest.raises(click.BadParameter) as exc_info:
                validate_positive(None, param, val)
            assert f'Значение {param} должно быть >= 0' in str(exc_info.value)
        else:
            assert validate_positive(None, param, val) == val


class TestProcessTableContent:
    """Класс тестов обработки табличного контента."""

    @pytest.fixture
    def sample_entity(self):
        """Пример правила переноса с выполнением Один раз."""
        return {
            'transfer_id': 123,
            'name': 'Test Entity',
            'query': {'source': 'src_table', 'destination': 'dst_table'},
            'crontab': {'start_at': '2025-01-01T12:55:55'},
            'status': 'active',
        }

    @pytest.fixture
    def sample_periodic_entity(self):
        """Пример периодического правила переноса."""
        return {
            'transfer_id': 1234,
            'name': 'Test Entity Periodic',
            'query': {'source': 'src_table', 'destination': 'dst_table'},
            'crontab': {
                'start_at': '2025-01-01T12:55:55',
                'period': 3,
            },
            'status': 'active',
        }

    def test_non_dict_entity_returns_empty_list(self):
        """Пустой список полей в результате некорректно переданного типа."""
        assert process_transfer_table_content(None, []) == []
        assert process_transfer_table_content('string', []) == []
        assert process_transfer_table_content(123, []) == []

    def test_empty_fields_returns_empty_list(self):
        """Пустое список полей приводит к пустому списку."""
        assert process_transfer_table_content({}, []) == []

    def test_source_field_extraction(self, sample_entity):
        """Отображение поля source."""
        fields = ['source']
        result = process_transfer_table_content(sample_entity, fields)
        assert result == ['src_table']

    def test_destination_field_extraction(self, sample_entity):
        """Отображение поля start_at."""
        fields = ['destination']
        result = process_transfer_table_content(sample_entity, fields)
        assert result == ['dst_table']

    def test_start_at_field_extraction(self, sample_entity):
        """Отображение поля start_at."""
        fields = ['start_at']
        result = process_transfer_table_content(sample_entity, fields)
        assert result == ['2025-01-01T12:55:55']

    def test_schedule_field_extraction(self, sample_periodic_entity):
        """Отображение полей по параметру scheduel."""
        fields = ['schedule']
        result = process_transfer_table_content(sample_periodic_entity, fields)
        assert result == ['Кажд. 3ч']

    def test_regular_field_extraction(self, sample_entity):
        """Извлечение часто встречающихся полей."""
        fields = ['transfer_id', 'name', 'status']
        result = process_transfer_table_content(sample_entity, fields)
        assert result == [123, 'Test Entity', 'active']

    def test_mixed_fields_extraction(self):
        """Поддержка нескольких полей."""
        entity = {
            'transfer_id': 12345,
            'name': 'Test Entity 3',
            'query': {'source': 'src_table', 'destination': 'dst_table'},
            'crontab': {
                'start_at': '2025-01-01T12:55:55',
                'time': '12:55',
                'weekdays': [1],
            },
            'status': 'active',
        }
        fields = ['source', 'schedule', 'status']
        result = process_transfer_table_content(entity, fields)
        assert result == ['src_table', 'Кажд. Пн в 12:55', 'active']

    def test_entity_without_crontab(self):
        """Поддержка отсутствующего поля crontab."""
        entity = {
            'query': {'source': 'src', 'destination': 'dst'},
            'status': 'inactive',
        }
        fields = ['source', 'schedule', 'start_at']
        result = process_transfer_table_content(entity, fields)
        assert result == ['src', 'Неизвестно', None]

    def test_empty_crontab_handling(self):
        """Поддержка пустого значения у поля crontab."""
        entity = {'crontab': {}, 'query': {'source': 'src'}}
        fields = ['schedule', 'source']
        result = process_transfer_table_content(entity, fields)
        assert result == ['Один раз', 'src']


class TestDisplayTransfers:
    """Класс тестов табличного отображения правил переноса."""

    @pytest.fixture
    def sample_data(self):
        """Имитация нескольких правил переноса в качестве данных."""
        return [
            {
                'name': 'Test Rule 1',
                'query': {'source': 'source_table_1', 'destination': 'dest_table_1'},
                'crontab': {
                    'start_at': '2023-01-01T12:55:55',
                    'time': '12:55',
                    'weekdays': [1],
                },
                'transfer_id': '123',
            },
            {
                'name': 'Test Rule 2',
                'query': {'source': 'source_table_2', 'destination': 'dest_table_2'},
                'crontab': {'start_at': '2023-01-02T12:00:00', 'period': 24},
                'transfer_id': '456',
            },
        ]

    def test_empty_data_returns_empty_table(self):
        """Отображение пустой таблицы при пустом ответе от апи."""
        result = display_transfers([], ['name'])
        assert result == '+---------+\n| Правило |\n+---------+\n+---------+'

    def test_empty_fields_uses_default_fields(self):
        """Отображение полей по умолчанию."""
        with patch('mls.manager.dts.table.TRANSFER_DEFAULT_FIELDS', {'name': 'Name'}):
            result = display_transfers([{'name': 'Test'}], [])
            assert 'Правило' in result
            assert 'Test' in result

    def test_field_name_substitution(self):
        """Отображение вложенных полей."""
        fields = ['name', 'source']
        result = display_transfers(
            [{'name': 'Test', 'query': {'source': 'src'}}], fields,
        )
        assert TRANSFER_FIELD_NAMES['name'] in result
        assert TRANSFER_FIELD_NAMES['source'] in result
        assert 'Test' in result
        assert 'src' in result

    def test_hyphen_in_field_names(self):
        """Отображение полей в случае с дефисом."""
        result = display_transfers([{'transfer_id': '123'}], ['transfer-id'])
        assert '123' in result
        assert TRANSFER_FIELD_NAMES['transfer-id'] in result

    def test_full(self, sample_data):
        """Отображение всех полей."""
        fields = ['name', 'source', 'destination', 'schedule', 'transfer-id']
        result = display_transfers(sample_data, fields)

        for field in fields:
            assert TRANSFER_FIELD_NAMES[field] in result

        assert 'Test Rule 1' in result
        assert 'source_table_1' in result
        assert 'dest_table_1' in result
        assert '123' in result
        assert 'Кажд. Пн в 12:55' in result
        assert 'Кажд. 24ч' in result

    def test_missing_fields_in_data(self):
        """Отсутствует отображеные несуществующих полей."""
        data = [{'name': 'Test'}]
        fields = ['name', 'nonexistent_field']
        result = display_transfers(data, fields)
        assert TRANSFER_FIELD_NAMES['name'] in result
        assert 'Test' in result
        assert 'None' in result or '' in result

    def test_tabulate_formatting(self, sample_data):
        """Отображение табличных признаков вместе с полями."""
        fields = ['name', 'source']
        result = display_transfers(sample_data, fields)
        assert '+' in result
        assert '|' in result
        assert TRANSFER_FIELD_NAMES['name'] in result
        assert TRANSFER_FIELD_NAMES['source'] in result

    def test_special_fields_processing(self, sample_data):
        """Отображение полей расписания."""
        fields = ['start_at', 'schedule']
        result = display_transfers(sample_data, fields)
        assert '2023-01-01T12:55:55' in result
        assert '2023-01-02T12:00:00' in result
        assert 'Кажд. Пн в 12:55' in result
        assert 'Кажд. 24ч' in result


class TestValidateInts:
    """Класс тестов для валидации целых значений."""
    @pytest.mark.parametrize(
        'value,min_val,max_val,expected',
        [(5, 1, 10, 5), (1, 1, 10, 1), (10, 1, 10, 10), (None, 1, 10, None)],
    )
    def test_valid_values(self, value, min_val, max_val, expected):
        """Корректные значения."""
        ctx = None
        param = None
        assert validate_ints(ctx, param, value, min_val, max_val) == expected

    @pytest.mark.parametrize(
        'value,min_val,max_val', [(0, 1, 10), (11, 1, 10), (-5, 0, 10), (100, 0, 99)],
    )
    def test_invalid_values(self, value, min_val, max_val):
        """Некорректные значения."""
        ctx = None
        param = None
        with pytest.raises(click.BadParameter) as excinfo:
            validate_ints(ctx, param, value, min_val, max_val)

        assert f'Число должно быть в пределах от {min_val} до {max_val}' in str(
            excinfo.value,
        )

    def test_min_greater_than_max(self):
        """Минимальное значение больше максимального."""
        ctx = None
        param = None
        with pytest.raises(click.BadParameter):
            validate_ints(ctx, param, 5, 10, 1)
