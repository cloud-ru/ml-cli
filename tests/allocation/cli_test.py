"""Интеграционные тесты для CLI команд аллокаций MLS."""
import json
import re

import pytest
import responses

from mls.cli import cli
from tests.allocation.data import ALLOC_LIST
from tests.allocation.data import INST_TYPES


class TestAllocationCli:
    """Тестовый класс для CLI команд аллокаций."""

    list_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/workspaces/v3/[^/\s]+/allocations')
    inst_types_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/allocations/[^/\s]+/instance-types')

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @pytest.mark.parametrize('data', [ALLOC_LIST, []])
    @responses.activate
    def test_list_json(self, runner, data):
        """Тест команды списка аллокаций с выводом в формате JSON."""
        responses.get(self.list_url, json=data)
        expected = json.dumps(data, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['allocation', 'list'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @pytest.mark.parametrize('data', [ALLOC_LIST, []])
    @responses.activate
    def test_list_text(self, runner, data):
        """Тест команды списка аллокаций с текстовым выводом."""
        responses.get(self.list_url, json=data)
        expected = str(data) + '\n'

        result = runner.invoke(cli, ['allocation', 'list', '--output', 'text'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @pytest.mark.parametrize('data', [INST_TYPES, []])
    @responses.activate
    def test_inst_types_json(self, runner, data):
        """Тест команды типов инстансов аллокаций с выводом в формате JSON."""
        responses.get(self.inst_types_url, json=data)
        expected = json.dumps(data, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['allocation', 'inst-types', '00000000-0000-4000-8000-000000000000'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @pytest.mark.parametrize('data', [INST_TYPES, []])
    @responses.activate
    def test_inst_types_text(self, runner, data):
        """Тест команды типов инстансов аллокаций с текстовым выводом."""
        responses.get(self.inst_types_url, json=data)
        expected = str(data) + '\n'

        result = runner.invoke(
            cli, ['allocation', 'inst-types', '00000000-0000-4000-8000-000000000000', '--output', 'text'],
        )

        assert result.exit_code == 0
        assert result.output == expected
