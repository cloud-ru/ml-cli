"""Тестовые сценарии для проверки работы команд transfer."""
import pytest

from mls.cli import cli


class TestTransfer:
    """Класс тестов правила переноса."""

    @pytest.mark.parametrize('opt_name, opt_value', [('weekday', '1'), ('period', '2')])
    def test_transfer_create(self, runner, mock_api_dts, opt_name, opt_value):
        """Проверка создания правила переноса."""
        result = runner.invoke(
            cli,
            [
                'transfer',
                'create',
                '--name',
                'ИмяПереноса',
                '--connector-id',
                '3c79fcd7-2b03-4472-93d8-50f4f121e8d6',
                '--dst-connector-id',
                '89dd8df1-ee3b-40c0-b517-bece7339a566',
                '--connector-type',
                's3custom',
                '--dst-connector-type',
                's3custom',
                '--cluster-name',
                'christofari-1',
                '--strategy',
                'write_all',
                '--source',
                'older1/other-subfolder',
                '--destination',
                'transfer-destination-folder',
                '--description',
                'Test-Description',
                f'--{opt_name}',
                opt_value,
            ],
        )
        assert result.exit_code == 0
        assert opt_name in result.output

    def test_transfer_create_negative(self, runner, mock_api_dts):
        """Негативная проверка создания правила переноса."""
        result = runner.invoke(
            cli,
            [
                'transfer',
                'create',
                '--name',
                'ИмяПереноса',
                '--connector-id',
                '3c79fcd7-2b03-4472-93d8-50f4f121e8d6',
                '--dst-connector-id',
                '89dd8df1-ee3b-40c0-b517-bece7339a566',
                '--connector-type',
                's3custom',
                '--dst-connector-type',
                's3custom',
                '--cluster-name',
                'christofari-1',
                '--strategy',
                'write_all',
                '--source',
                'older1/other-subfolder',
                '--destination',
                'transfer-destination-folder',
                '--description',
                'Test-Description',
                '--weekday',
                1,
                '--period',
                1,
            ],
        )
        assert result.exit_code == 2
        assert (
            'Для создания правила периодического переноса '
            'может быть передана только одна из опций расписания --weekday, --monthday, --period'
        ) in result.output

    @pytest.mark.parametrize(
        'transfer_id_1, transfer_id_2',
        [
            (
                '40e36b8d-cb6c-4726-8e8c-2b1d51285934',
                'f6c75f1b-2559-4eed-a982-5acb6c4439ce',
            ),
        ],
    )
    def test_transfer_delete(self, runner, mock_api_dts, transfer_id_1, transfer_id_2):
        """Удаление правил переноса."""
        result = runner.invoke(
            cli,
            [
                'transfer',
                'delete',
                transfer_id_1,
                transfer_id_2,
            ],
        )
        assert result.exit_code == 0
        assert transfer_id_1 in result.output
        assert transfer_id_2 in result.output

    @pytest.mark.parametrize('output', ['json', 'text'])
    def test_transfer_list(self, runner, mock_api_dts, output):
        """Получение списка правил переноса."""
        result = runner.invoke(cli, ['transfer', 'list', '-O', output])
        assert result.exit_code == 0
        assert '40e36b8d-cb6c-4726-8e8c-2b1d51285934' in result.output
        assert 'f6c75f1b-2559-4eed-a982-5acb6c4439ce' in result.output

    @pytest.mark.parametrize('transfer_id', ['40e36b8d-cb6c-4726-8e8c-2b1d51285934'])
    def test_transfer_get(self, runner, mock_api_dts, transfer_id):
        """Получения информации о правиле переноса."""
        result = runner.invoke(cli, ['transfer', 'get', '--transfer-id', transfer_id])
        assert result.exit_code == 0
        assert transfer_id in result.output

    def test_transfer_activate(self, runner, mock_api_dts):
        """Активация неактивного правила переноса."""
        result = runner.invoke(
            cli,
            [
                'transfer',
                'activate',
                '--transfer-id',
                '40e36b8d-cb6c-4726-8e8c-2b1d51285934',
            ],
        )
        assert result.exit_code == 0

    def test_transfer_deactivate(self, runner, mock_api_dts):
        """Деактивация периодического правила переноса."""
        result = runner.invoke(
            cli,
            [
                'transfer',
                'deactivate',
                '--transfer-id',
                '40e36b8d-cb6c-4726-8e8c-2b1d51285934',
            ],
        )
        assert result.exit_code == 0
        assert "'active': False" in result.output

    def test_transfer_cancel(self, runner, mock_api_dts):
        """Проверка отмены правила переноса."""
        result = runner.invoke(
            cli,
            [
                'transfer',
                'stop',
                '--transfer-id',
                '40e36b8d-cb6c-4726-8e8c-2b1d51285934',
                '--execution-date',
                '2025-01-01T12:55:55',
            ],
        )
        assert result.exit_code == 0
        assert 'cancelled' in result.output

    def test_transfer_logs(self, runner, mock_api_dts):
        """Проверка логов правила переноса."""
        history_id = '769e3712-754d-474a-8cc8-f09f18bf092c'
        transfer_id = '40e36b8d-cb6c-4726-8e8c-2b1d51285934'
        result = runner.invoke(
            cli,
            [
                'transfer',
                'logs',
                '--transfer-id',
                transfer_id,
                '--history-id',
                history_id,
            ],
        )
        assert result.exit_code == 0
        assert history_id, transfer_id in result.output

    def test_transfer_logs_negative(self, runner, mock_api_dts):
        """Негативная проверка логов правила переноса."""
        result = runner.invoke(
            cli,
            [
                'transfer',
                'logs',
            ],
        )
        assert result.exit_code == 2

    def test_transfer_history(self, runner, mock_api_dts):
        """История запусков правила переноса."""
        transfer_id = '40e36b8d-cb6c-4726-8e8c-2b1d51285934'
        source_name = 'manifest.yaml'
        result = runner.invoke(
            cli,
            ['transfer', 'history', '--transfer-id', transfer_id, '--source-name', source_name],
        )
        assert result.exit_code == 0
        assert transfer_id, source_name in result.output

    @pytest.mark.parametrize(
        'params, res',
        [
            (
                [
                    '--transfer-id',
                    '40e36b8d-cb6c-4726-8e8c-2b1d51285934',
                    '--connector-id',
                    'updated-connector',
                    '--dst-connector-id',
                    'update-dst-connector',
                    '--name',
                    'updated-name',
                    '--source',
                    'folder1,folder2',
                    '--destination',
                    'updated-folder',
                    '--period',
                    2,
                ],
                0,
            ),
            ([], 1),
        ],
    )
    def test_transfer_update(self, runner, mock_api_dts, params, res):
        """Обновление правила переноса."""
        result = runner.invoke(cli, ['transfer', 'update', *params])
        assert result.exit_code == res
