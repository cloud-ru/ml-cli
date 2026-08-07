"""Интеграционные тесты для CLI-команды workspace."""
import json
import re

import pytest
import responses

from mls.cli import cli
from tests.workspace.data import WORKSPACES_RESPONSE


class TestWorkspaceCli:
    """Тестовый класс для CLI-команды workspace."""

    workspaces_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/workspaces/v3/')

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_ws_json(self, runner):
        """Workspace manager получает namespaces/workspaces через Public API."""
        responses.get(self.workspaces_url, json=WORKSPACES_RESPONSE)
        expected = json.dumps(WORKSPACES_RESPONSE, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['ws', 'list'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_ws_passes_customer_id(self, runner):
        """Workspace manager прокидывает фильтр customer_id как в Public API."""
        responses.get(
            self.workspaces_url,
            match=[responses.matchers.query_param_matcher({'customer_id': 'customer-1'})],
            json=WORKSPACES_RESPONSE,
        )

        result = runner.invoke(cli, ['ws', 'list', '--customer-id', 'customer-1'])

        assert result.exit_code == 0

    def test_ws_help(self, runner):
        """Workspace manager показывает help в общем стиле CLI."""
        result = runner.invoke(cli, ['ws', 'list', '--help'])

        assert result.exit_code == 0
        assert 'Отображение workspaces.' in result.output
        assert 'Управление Jupyter Server.' not in result.output
        assert '--customer-id' in result.output
