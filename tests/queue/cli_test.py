"""Интеграционные тесты для CLI команд очередей MLS."""
import json
import re

import pytest
import responses

from mls.cli import cli
from tests.queue.data import INST_TYPES
from tests.queue.data import QUEUE_LIST


class TestQueueCli:
    """Тестовый класс для CLI команд очередей."""

    list_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/workspaces/v3/[^/\s]+/allocations/[^/\s]+/queues')
    inst_types_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/queues/[^/\s]+/instance-types')

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @pytest.mark.parametrize('data', [QUEUE_LIST, []])
    @responses.activate
    def test_list_json(self, runner, data):
        """Тест команды списка очередей с выводом в формате JSON."""
        responses.get(self.list_url, json=data)
        expected = json.dumps(data, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['queue', 'list', '00000000-0000-4000-8000-000000000000'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @pytest.mark.parametrize('data', [QUEUE_LIST, []])
    @responses.activate
    def test_list_text(self, runner, data):
        """Тест команды списка очередей с текстовым выводом."""
        responses.get(self.list_url, json=data)
        expected = str(data) + '\n'

        result = runner.invoke(cli, ['queue', 'list', '00000000-0000-4000-8000-000000000000', '--output', 'text'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @pytest.mark.parametrize('data', [INST_TYPES, []])
    @responses.activate
    def test_inst_types_json(self, runner, data):
        """Тест команды типов инстансов очередей с выводом в формате JSON."""
        responses.get(self.inst_types_url, json=data)
        expected = json.dumps(data, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['queue', 'inst-types', '22222222-2222-4222-a222-222222222222'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @pytest.mark.parametrize('data', [INST_TYPES, []])
    @responses.activate
    def test_inst_types_text(self, runner, data):
        """Тест команды типов инстансов очередей с текстовым выводом."""
        responses.get(self.inst_types_url, json=data)
        expected = str(data) + '\n'

        result = runner.invoke(cli, ['queue', 'inst-types', '22222222-2222-4222-a222-222222222222', '--output', 'text'])

        assert result.exit_code == 0
        assert result.output == expected
