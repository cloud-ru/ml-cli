"""Тестовые сценарии для проверки работы команд connector."""
import pytest

from mls.cli import cli
from tests.dts.conftest import mock_validate_connector_not_exists


class TestConnector:
    """Класс тестов коннектора."""

    @pytest.mark.parametrize('out', ['text', 'json'])
    def test_connector_list(self, runner, mock_api_dts, out):
        """Проверка метода получения списка коннекторов."""
        result = runner.invoke(cli, ['connector', 'list', '-O', out])
        assert result.exit_code == 0

    def test_connector_create(self, runner, mock_api_dts):
        """Проверка метода создания коннектора."""
        result = runner.invoke(
            cli,
            ['connector', 'create', '--connector-type', 's3custom', '--public'],
            input='some-fake-endpoint.com\n\ns3bucket\n\ns3AK\n\ns3SK\n\nName\n\n',
        )
        assert result.exit_code == 0

    def test_connector_update(self, runner, mock_api_dts):
        """Проверка метода обновления коннектора."""
        result = runner.invoke(
            cli,
            'connector update --connector-type s3custom',
            input='9e12966e-2713-49b2-9cd5-21e0e7b82c5a\n\nendpoint\n\nbucket\n\nS3AK\n\nS3SK\n\nName\n\n',
        )
        assert result.exit_code == 0

    def test_connector_update_not_found(self, runner, mock_api_dts, monkeypatch):
        """Негативная проверка метода обновления коннектора."""
        monkeypatch.setattr(
            'mls.manager.dts.connector_cli.validate_connector_exists',
            mock_validate_connector_not_exists,
        )

        result = runner.invoke(
            cli,
            'connector update --connector-type s3custom',
            input='9e12966e-2713-49b2-9cd5-21e0e7b82c5c\n\n',
        )

        assert result.exit_code == 2

    def test_connector_sources(self, runner, mock_api_dts):
        """Проверка метода получения схем типов коннектора."""
        result = runner.invoke(cli, 'connector sources')
        assert result.exit_code == 0
        assert (
            result.output
            == "[{'source_type': 's3mlspace', 'source_name': 'S3 ML Space'}]\n"
        )

    def test_conn_activate(self, runner, mock_api_dts):
        """Проверка метода активации коннектора."""
        result = runner.invoke(
            cli,
            'connector activate --connector-type s3custom --connector-id 58577044-64c7-41eb-9993-edafab55829c',
        )
        assert result.exit_code == 0

    def test_conn_deactivate(self, runner, mock_api_dts):
        """Проверка метода деактивации коннектора."""
        result = runner.invoke(
            cli,
            'connector deactivate --connector-type s3custom --connector-id 58577044-64c7-41eb-9993-edafab55829c',
        )
        assert result.exit_code == 0

    def test_conn_delete(self, runner, mock_api_dts):
        """Проверка метода удаления коннектора."""
        result = runner.invoke(
            cli, 'connector delete 58577044-64c7-41eb-9993-edafab55829c',
        )

        assert result.exit_code == 0
        assert '58577044-64c7-41eb-9993-edafab55829c' in result.output
