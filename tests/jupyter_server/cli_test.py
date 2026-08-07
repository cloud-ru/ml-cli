"""Интеграционные тесты для CLI команд jupyter-server MLS."""
import json
import re
from urllib.parse import parse_qs
from urllib.parse import urlparse

import pytest
import responses
from responses import activate
from responses import delete
from responses import get
from responses import matchers
from responses import post

from mls.cli import cli
from tests.jupyter_server.data import ASYNC_RESULT
from tests.jupyter_server.data import AUTOSHUTDOWN_RULE
from tests.jupyter_server.data import CONFIG_RESPONSE
from tests.jupyter_server.data import JUPYTER_SERVER_DETAIL
from tests.jupyter_server.data import JUPYTER_SERVER_LIST


class TestJupyterServerCli:
    """Тестовый класс для CLI команд jupyter servers."""

    list_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/notebooks/v2/notebooks')
    create_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/notebooks/v2/[^/\s]+/notebook')
    get_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/notebooks/v1/notebook/[^/\s]+')
    delete_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/notebooks/v2/notebook/[^/\s]+')
    pause_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/notebooks/v2/notebook/[^/\s]+/pause')
    modify_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/notebooks/v2/notebook/[^/\s]+/modify')
    resume_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/notebooks/v1/[^/\s]+/notebook/[^/\s]+/resume')
    autoshutdown_v2_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/notebooks/v2/autoshutdown-rules/workspace/[^/\s]+')
    autoshutdown_v1_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/notebooks/v1/autoshutdown-rules/workspace/[^/\s]+')
    config_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/configs\?cluster_type=MT')

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_config_uses_public_api_configs_mt(self, runner):
        """Jupyter config получает регионы и instance types через Public API /configs."""
        get(self.config_url, json=CONFIG_RESPONSE)
        expected = json.dumps(CONFIG_RESPONSE, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['js', 'config'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_config_accepts_workspace_id_argument(self, runner):
        """Jupyter config может переопределить x-workspace-id из аргумента."""
        workspace_id = '11111111-1111-4111-8111-111111111111'
        get(self.config_url, json=CONFIG_RESPONSE)

        result = runner.invoke(cli, ['js', 'config', workspace_id])

        assert result.exit_code == 0
        assert responses.calls[-1].request.headers['x-workspace-id'] == workspace_id

    def test_js_help_texts_are_polished(self, runner):
        """Jupyter help содержит согласованные описания без опечаток."""
        config_help = runner.invoke(cli, ['js', 'config', '--help'])
        yaml_help = runner.invoke(cli, ['js', 'yaml', '--help'])
        get_help = runner.invoke(cli, ['js', 'get', '--help'])

        assert config_help.exit_code == 0
        assert yaml_help.exit_code == 0
        assert get_help.exit_code == 0
        normalized_config_help = ' '.join(config_help.output.split())
        normalized_yaml_help = ' '.join(yaml_help.output.split())
        normalized_get_help = ' '.join(get_help.output.split())
        assert 'Отображает информацию о доступных регионах, инстанс типах и образах для Jupyter Server.' in normalized_config_help
        assert 'Команда для генерации примера YAML-манифеста для создания или перезапуска Jupyter Server.' in normalized_yaml_help
        assert 'Сгенерировать пример манифеста для перезапуска Jupyter Server' in normalized_yaml_help
        assert 'информации о Jupyter Server' in normalized_get_help
        assert 'инфомации' not in normalized_get_help

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_list_json(self, runner):
        """Тест команды списка jupyter servers с выводом в формате JSON."""
        get(self.list_url, json=JUPYTER_SERVER_LIST)
        expected = json.dumps(JUPYTER_SERVER_LIST, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['js', 'list'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_list_text(self, runner):
        """Тест команды списка jupyter servers с текстовым выводом."""
        get(self.list_url, json=JUPYTER_SERVER_LIST)
        expected = str(JUPYTER_SERVER_LIST) + '\n'

        result = runner.invoke(cli, ['js', 'list', '--output', 'text'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_list_query_params(self, runner):
        """Jupyter list прокидывает query-параметры Public API из Swagger."""
        get(self.list_url, json=JUPYTER_SERVER_LIST)

        result = runner.invoke(
            cli,
            [
                'js',
                'list',
                '--notebook-type',
                'jupyter',
                '--order_by',
                'name',
                '--desc',
                '--limit',
                '10',
                '--offset',
                '5',
                '--search',
                'demo',
                '--status',
                'running,paused',
                '--access_mode',
                'private',
            ],
        )

        assert result.exit_code == 0
        query = parse_qs(urlparse(responses.calls[-1].request.url).query)
        assert query == {
            'notebook_type': ['jupyter'],
            'order_by': ['name'],
            'desc': ['True'],
            'limit': ['10'],
            'offset': ['5'],
            'search': ['demo'],
            'status': ['running,paused'],
            'access_mode': ['private'],
        }

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_get_json(self, runner):
        """Тест команды получения jupyter servers по uuid."""
        get(self.get_url, json=JUPYTER_SERVER_DETAIL)
        expected = json.dumps(JUPYTER_SERVER_DETAIL, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['js', 'get', '11111111-1111-4111-8111-111111111111'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile')
    @pytest.mark.parametrize(
        'argv',
        [
            ['js', 'get', 'invalid-uuid'],
            ['js', 'delete', 'invalid-uuid'],
            ['js', 'pause', 'invalid-uuid'],
            ['js', 'modify', 'invalid-uuid', '--shutdown-in', '1'],
            ['js', 'resume', '--namespace', 'default', '--instance-type', 'free.0gpu', 'invalid-uuid'],
        ],
    )
    def test_jupyter_server_commands_reject_invalid_uuid(self, runner, argv):
        """Некорректный UUID: Click отклоняет до HTTP, код 2 и сообщение об ошибке."""
        result = runner.invoke(cli, argv)
        assert result.exit_code == 2
        assert 'not a valid UUID' in result.output

    @pytest.mark.usefixtures('test_profile')
    @pytest.mark.parametrize(
        'argv',
        [
            ['js', 'get', ''],
            ['js', 'delete', ''],
            ['js', 'pause', ''],
            ['js', 'modify', '', '--shutdown-in', '1'],
            ['js', 'resume', '--namespace', 'default', ''],
        ],
    )
    def test_jupyter_server_commands_reject_empty_uuid(self, runner, argv):
        """Пустая строка вместо UUID: ненулевой код и явная ошибка валидации."""
        result = runner.invoke(cli, argv)
        assert result.exit_code == 2
        assert 'not a valid UUID' in result.output

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_create_with_options(self, runner):
        """Тест команды создания jupyter servers с параметрами CLI."""
        create_body = {
            'name': 'nb-1',
            'image': {'name': 'cr.example/img', 'tag': '1.0', 'type': 'datahub'},
            'instance_type': 'free.0gpu',
            'region': 'test_region',
            'postponed_pause_enabled': False,
        }
        post(
            self.create_url,
            match=[matchers.json_params_matcher(create_body)],
            json=ASYNC_RESULT,
        )
        expected = json.dumps(ASYNC_RESULT, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(
            cli,
            [
                'js',
                'create',
                '--namespace',
                'default',
                '--name',
                'nb-1',
                '--image-name',
                'cr.example/img',
                '--image-tag',
                '1.0',
                '--image-type',
                'datahub',
                '--instance-type',
                'free.0gpu',
            ],
        )

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_create_with_config_manifest(self, runner, tmp_path):
        """Create через --config: тело и namespace только из YAML."""
        manifest = (
            """
            namespace: ns-from-file
            jupyter_server:
                name: nb-cfg
                image:
                    name: cr.example/img
                    tag: "1.0"
                    type: datahub
                instance_type: free.0gpu
                region: DGX2-MT
                postponed_pause_enabled: false
            """
        )
        path = tmp_path / 'jupyter_create.yaml'
        path.write_text(manifest, encoding='utf-8')
        create_body = {
            'name': 'nb-cfg',
            'image': {'name': 'cr.example/img', 'tag': '1.0', 'type': 'datahub'},
            'instance_type': 'free.0gpu',
            'region': 'DGX2-MT',
            'postponed_pause_enabled': False,
        }
        post(
            self.create_url,
            match=[matchers.json_params_matcher(create_body)],
            json=ASYNC_RESULT,
        )
        expected = json.dumps(ASYNC_RESULT, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['js', 'create', '--config', str(path)])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_create_accepts_generated_sample_config(self, runner):
        """Сгенерированный sample Jupyter Server create принимается через --config."""
        post(self.create_url, json=ASYNC_RESULT)

        result = runner.invoke(
            cli,
            ['js', 'create', '--config', './samples/template.jupyter_server_create.yaml'],
        )

        assert result.exit_code == 0
        assert '/notebooks/v2/default/notebook' in responses.calls[-1].request.url
        assert json.loads(responses.calls[-1].request.body) == {
            'name': 'my-notebook',
            'image': {
                'name': 'cr.ai.cloud.ru/aicloud-jupyter/jupyter-server',
                'tag': 'latest',
                'type': 'datahub',
            },
            'instance_type': 'free.0gpu',
            'region': 'test_region',
            'postponed_pause_enabled': False,
            'allocation_name': 'my-allocation',
            'queue_name': 'my-queue',
            'description': 'Описание Jupyter Server',
            'pause_at': '45 * * * *',
            's3_buckets': [{'bucket_name': 'bucket-name', 'access_rule': 'ro'}],
            's3_credentials': {
                's3_credentials_source': 'iam-product-sa',
                's3_tenant_id': 'tenant_id',
            },
        }

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_create_config_allows_cli_override(self, runner, tmp_path):
        """С --config явно переданные CLI-опции переопределяют YAML."""
        manifest = (
            """
            namespace: default
            jupyter_server:
                name: n
                image:
                    name: i
                    tag: t
                    type: custom
                instance_type: free.0gpu
                region: DGX2-MT
            """
        )
        path = tmp_path / 'm.yaml'
        path.write_text(manifest, encoding='utf-8')
        create_body = {
            'name': 'n-override',
            'image': {'name': 'i', 'tag': 't', 'type': 'custom'},
            'instance_type': 'a100.1gpu',
            'region': 'SR006',
            'postponed_pause_enabled': False,
        }
        post(
            self.create_url,
            match=[matchers.json_params_matcher(create_body)],
            json=ASYNC_RESULT,
        )

        result = runner.invoke(
            cli,
            [
                'js',
                'create',
                '--config',
                str(path),
                '--namespace',
                'other',
                '--name',
                'n-override',
                '--instance-type',
                'a100.1gpu',
                '--region',
                'SR006',
            ],
        )

        assert result.exit_code == 0
        assert '/notebooks/v2/other/notebook' in responses.calls[-1].request.url

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_create_accepts_region_from_public_config_not_local_choice(self, runner):
        """Jupyter create не ограничивает region старой локальной константой."""
        post(self.create_url, json=ASYNC_RESULT)

        result = runner.invoke(
            cli,
            [
                'js',
                'create',
                '--namespace',
                'default',
                '--name',
                'nb-1',
                '--image-name',
                'cr.example/img',
                '--image-tag',
                '1.0',
                '--image-type',
                'datahub',
                '--instance-type',
                'free.0gpu',
                '--region',
                'NEW-MT-REGION',
            ],
        )

        assert result.exit_code == 0
        assert json.loads(responses.calls[-1].request.body)['region'] == 'NEW-MT-REGION'

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_resume_with_config_manifest(self, runner, tmp_path):
        """Resume через --config: namespace и тело запроса только из YAML."""
        manifest = (
            """
            namespace: ns-resume-file
            resume:
                region: SR006
                instance_type: free.0gpu
            """
        )
        path = tmp_path / 'jupyter_resume.yaml'
        path.write_text(manifest, encoding='utf-8')
        resume_body = {'region': 'SR006', 'instance_type': 'free.0gpu'}
        post(
            self.resume_url,
            match=[matchers.json_params_matcher(resume_body)],
            json=JUPYTER_SERVER_DETAIL,
        )
        expected = json.dumps(JUPYTER_SERVER_DETAIL, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(
            cli,
            ['js', 'resume', '--config', str(path), '11111111-1111-4111-8111-111111111111'],
        )

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_resume_accepts_generated_sample_config(self, runner):
        """Сгенерированный sample Jupyter Server resume принимается через --config."""
        post(self.resume_url, json=JUPYTER_SERVER_DETAIL)

        result = runner.invoke(
            cli,
            [
                'js',
                'resume',
                '--config',
                './samples/template.jupyter_server_resume.yaml',
                '11111111-1111-4111-8111-111111111111',
            ],
        )

        assert result.exit_code == 0
        assert '/notebooks/v1/default/notebook/11111111-1111-4111-8111-111111111111/resume' in responses.calls[-1].request.url
        assert json.loads(responses.calls[-1].request.body) == {
            'region': 'test_region',
            'instance_type': 'free.0gpu',
        }

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_resume_config_allows_cli_override(self, runner, tmp_path):
        """С --config явно переданные CLI-опции resume переопределяют YAML."""
        manifest = (
            """
            namespace: default
            resume:
                region: SR006
                instance_type: free.0gpu
            """
        )
        path = tmp_path / 'r.yaml'
        path.write_text(manifest, encoding='utf-8')
        resume_body = {'region': 'SR008', 'instance_type': 'a100.1gpu'}
        post(
            self.resume_url,
            match=[matchers.json_params_matcher(resume_body)],
            json=JUPYTER_SERVER_DETAIL,
        )

        result = runner.invoke(
            cli,
            [
                'js',
                'resume',
                '--config',
                str(path),
                '--namespace',
                'other',
                '--region',
                'SR008',
                '--instance-type',
                'a100.1gpu',
                '11111111-1111-4111-8111-111111111111',
            ],
        )

        assert result.exit_code == 0
        assert '/notebooks/v1/other/notebook/' in responses.calls[-1].request.url

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_resume_missing_namespace(self, runner):
        """Resume без --config и без --namespace: ошибка до HTTP."""
        result = runner.invoke(cli, ['js', 'resume', '11111111-1111-4111-8111-111111111111'])
        assert result.exit_code == 2
        assert 'Отсутствуют обязательные опции' in result.output
        assert '--namespace' in result.output

    @activate
    def test_js_yaml_prints_manifest_contract(self, runner):
        """Команда js yaml печатает пример namespace + jupyter_server."""
        result = runner.invoke(cli, ['js', 'yaml'])

        assert result.exit_code == 0
        assert 'namespace:' in result.output
        assert 'jupyter_server:' in result.output

    @activate
    def test_js_yaml_resume_prints_manifest_contract(self, runner):
        """Команда js yaml --resume печатает пример namespace + resume."""
        result = runner.invoke(cli, ['js', 'yaml', '--resume'])

        assert result.exit_code == 0
        assert 'namespace:' in result.output
        assert 'resume:' in result.output
        assert 'instance_type:' in result.output
        assert 'reason:' not in result.output

    def test_resume_help_does_not_expose_unsupported_reason(self, runner):
        """Jupyter resume не публикует поля вне backend ResumeNotebookPayload."""
        result = runner.invoke(cli, ['js', 'resume', '--help'])

        assert result.exit_code == 0
        assert '--reason' not in result.output

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @pytest.mark.parametrize(
        'extra_argv, expected_flag',
        [
            ([], '--namespace'),
            (['--namespace', 'default'], '--name'),
            (['--namespace', 'default', '--name', 'nb-1'], '--image-name'),
            (['--namespace', 'default', '--name', 'nb-1', '--image-name', 'cr.example/img'], '--image-tag'),
            (
                [
                    '--namespace',
                    'default',
                    '--name',
                    'nb-1',
                    '--image-name',
                    'cr.example/img',
                    '--image-tag',
                    '1.0',
                ],
                '--image-type',
            ),
            (
                [
                    '--namespace',
                    'default',
                    '--name',
                    'nb-1',
                    '--image-name',
                    'cr.example/img',
                    '--image-tag',
                    '1.0',
                    '--image-type',
                    'datahub',
                ],
                '--instance-type',
            ),
        ],
    )
    @activate
    def test_create_missing_required_options(self, runner, extra_argv, expected_flag):
        """Create без части обязательных опций: код 2 и перечень недостающих опций."""
        result = runner.invoke(cli, ['js', 'create', *extra_argv])
        assert result.exit_code == 2
        assert 'Отсутствуют обязательные опции' in result.output
        assert expected_flag in result.output

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_create_with_optional_api_fields(self, runner):
        """Тест создания с полями контракта Public API (allocation, queue, S3, pause)."""
        s3_buckets = [{'bucket_name': 'b1', 'access_rule': 'ro'}]
        s3_credentials = {'s3_credentials_source': 'iam-product-sa', 's3_tenant_id': 'tenant_id'}
        create_body = {
            'name': 'nb-2',
            'image': {'name': 'img', 'tag': 'v1', 'type': 'custom'},
            'instance_type': 'free.0gpu',
            'region': 'SR006',
            'postponed_pause_enabled': True,
            'allocation_name': 'alloc-1',
            'queue_name': 'queue-1',
            'description': 'Test server',
            'pause_at': '45 * * * *',
            's3_buckets': s3_buckets,
            's3_credentials': s3_credentials,
        }
        post(
            self.create_url,
            match=[matchers.json_params_matcher(create_body)],
            json=ASYNC_RESULT,
        )
        expected = json.dumps(ASYNC_RESULT, indent=4, ensure_ascii=False) + '\n'
        buckets_arg = json.dumps(s3_buckets, separators=(',', ':'))
        creds_arg = json.dumps(s3_credentials, separators=(',', ':'))

        result = runner.invoke(
            cli,
            [
                'js',
                'create',
                '--namespace',
                'ns1',
                '--name',
                'nb-2',
                '--image-name',
                'img',
                '--image-tag',
                'v1',
                '--image-type',
                'custom',
                '--instance-type',
                'free.0gpu',
                '--region',
                'SR006',
                '--allocation-name',
                'alloc-1',
                '--queue-name',
                'queue-1',
                '--description',
                'Test server',
                '--pause-at',
                '45 * * * *',
                '--postponed-pause-enabled',
                '--s3-buckets-json',
                buckets_arg,
                '--s3-credentials-json',
                creds_arg,
            ],
        )

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    def test_create_invalid_s3_buckets_json(self, runner):
        """Тест отклонения невалидного JSON для s3_buckets."""
        result = runner.invoke(
            cli,
            [
                'js',
                'create',
                '--namespace',
                'default',
                '--name',
                'x',
                '--image-name',
                'i',
                '--image-tag',
                't',
                '--image-type',
                'custom',
                '--instance-type',
                'free.0gpu',
                '--s3-buckets-json',
                '{"not": "array"}',
            ],
        )
        assert result.exit_code != 0

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    def test_create_rejects_invalid_image_type(self, runner):
        """Jupyter create принимает только image.type из backend enum."""
        result = runner.invoke(
            cli,
            [
                'js',
                'create',
                '--namespace',
                'default',
                '--name',
                'x',
                '--image-name',
                'i',
                '--image-tag',
                't',
                '--image-type',
                'unsupported',
                '--instance-type',
                'free.0gpu',
            ],
        )

        assert result.exit_code == 2
        assert 'unsupported' in result.output

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_delete_notebook(self, runner):
        """Тест команды удаления jupyter servers."""
        delete(self.delete_url, json=ASYNC_RESULT)
        expected = json.dumps(ASYNC_RESULT, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['js', 'delete', '11111111-1111-4111-8111-111111111111'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_pause_notebook(self, runner):
        """Тест команды паузы jupyter servers."""
        post(self.pause_url, json=JUPYTER_SERVER_DETAIL)
        expected = json.dumps(JUPYTER_SERVER_DETAIL, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['js', 'pause', '11111111-1111-4111-8111-111111111111'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_modify_autoshutdown_timer(self, runner):
        """Тест команды изменения jupyter servers (autoshutdown по таймеру)."""
        modify_body = {
            'autoshutdown_config': {
                'by_timer': {'shutdown_in': 1200, 'is_enabled': True},
            },
        }
        post(
            self.modify_url,
            match=[matchers.json_params_matcher(modify_body)],
            json=ASYNC_RESULT,
        )
        expected = json.dumps(ASYNC_RESULT, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(
            cli,
            ['js', 'modify', '11111111-1111-4111-8111-111111111111', '--shutdown-in', '1200'],
        )

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_modify_autoshutdown_timer_disabled(self, runner):
        """Тест изменения autoshutdown с выключенным таймером."""
        modify_body = {
            'autoshutdown_config': {
                'by_timer': {'shutdown_in': 60, 'is_enabled': False},
            },
        }
        post(
            self.modify_url,
            match=[matchers.json_params_matcher(modify_body)],
            json=ASYNC_RESULT,
        )
        expected = json.dumps(ASYNC_RESULT, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(
            cli,
            [
                'js',
                'modify',
                '11111111-1111-4111-8111-111111111111',
                '--shutdown-in',
                '60',
                '--timer-disabled',
            ],
        )

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_resume_with_options(self, runner):
        """Тест команды возобновления jupyter servers с параметрами CLI."""
        resume_body = {'region': 'SR006', 'instance_type': 'free.0gpu'}
        post(
            self.resume_url,
            match=[matchers.json_params_matcher(resume_body)],
            json=JUPYTER_SERVER_DETAIL,
        )
        expected = json.dumps(JUPYTER_SERVER_DETAIL, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(
            cli,
            [
                'js',
                'resume',
                '--namespace',
                'default',
                '--region',
                'SR006',
                '--instance-type',
                'free.0gpu',
                '11111111-1111-4111-8111-111111111111',
            ],
        )

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_modify_without_changes_errors(self, runner):
        """Тест: modify без ни одного поля — ошибка (responses: client запрашивает token при init)."""
        result = runner.invoke(cli, ['js', 'modify', '11111111-1111-4111-8111-111111111111'])
        assert result.exit_code != 0

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_modify_autoshutdown_config_json(self, runner):
        """Тест modify с полным autoshutdown_config (JSON)."""
        cfg = {'by_schedule': {'shutdown_at': '45 * * * *', 'is_enabled': True}}
        modify_body = {'autoshutdown_config': cfg}
        post(
            self.modify_url,
            match=[matchers.json_params_matcher(modify_body)],
            json=ASYNC_RESULT,
        )
        expected = json.dumps(ASYNC_RESULT, indent=4, ensure_ascii=False) + '\n'
        arg = json.dumps(cfg, separators=(',', ':'))

        result = runner.invoke(
            cli,
            [
                'js',
                'modify',
                '11111111-1111-4111-8111-111111111111',
                '--autoshutdown-config-json',
                arg,
            ],
        )
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_modify_description_and_s3(self, runner):
        """Тест modify: description и S3."""
        s3_buckets = [{'bucket_name': 'b', 'access_rule': 'ro'}]
        s3_credentials = {'s3_credentials_source': 'not-enabled'}
        modify_body = {
            'description': 'New desc',
            's3_buckets': s3_buckets,
            's3_credentials': s3_credentials,
        }
        post(
            self.modify_url,
            match=[matchers.json_params_matcher(modify_body)],
            json=ASYNC_RESULT,
        )
        expected = json.dumps(ASYNC_RESULT, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(
            cli,
            [
                'js',
                'modify',
                '11111111-1111-4111-8111-111111111111',
                '--description',
                'New desc',
                '--s3-buckets-json',
                json.dumps(s3_buckets, separators=(',', ':')),
                '--s3-credentials-json',
                json.dumps(s3_credentials, separators=(',', ':')),
            ],
        )
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_resume_requires_instance_type_without_config(self, runner):
        """Resume без --config требует явный --instance-type."""
        result = runner.invoke(
            cli,
            [
                'js',
                'resume',
                '--namespace',
                'default',
                '11111111-1111-4111-8111-111111111111',
            ],
        )
        assert result.exit_code == 2
        assert '--instance-type' in result.output

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_autoshutdown_set_by_schedule_json(self, runner):
        """Тест autoshutdown set только с by_schedule (JSON)."""
        by_schedule = {'shutdown_at': '0 12 * * *', 'is_enabled': True}
        post_body = {'by_schedule': by_schedule}
        post(
            self.autoshutdown_v2_url,
            match=[matchers.json_params_matcher(post_body)],
            json=AUTOSHUTDOWN_RULE,
        )
        expected = json.dumps(AUTOSHUTDOWN_RULE, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(
            cli,
            [
                'js',
                'autoshutdown',
                'set',
                '00000000-0000-4000-8000-000000000000',
                '--by-schedule-json',
                json.dumps(by_schedule, separators=(',', ':')),
            ],
        )
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_autoshutdown_get_v2(self, runner):
        """Тест команды получения autoshutdown правила."""
        get(self.autoshutdown_v2_url, json=AUTOSHUTDOWN_RULE)
        expected = json.dumps(AUTOSHUTDOWN_RULE, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['js', 'autoshutdown', 'get', '00000000-0000-4000-8000-000000000000'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_autoshutdown_set_v2_with_options(self, runner):
        """Тест команды создания autoshutdown правила с параметрами CLI."""
        post(
            self.autoshutdown_v2_url,
            match=[matchers.json_params_matcher(AUTOSHUTDOWN_RULE)],
            json=AUTOSHUTDOWN_RULE,
        )
        expected = json.dumps(AUTOSHUTDOWN_RULE, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(
            cli,
            [
                'js',
                'autoshutdown',
                'set',
                '00000000-0000-4000-8000-000000000000',
                '--shutdown-in',
                '3600',
            ],
        )

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @activate
    def test_autoshutdown_delete(self, runner):
        """Тест команды удаления autoshutdown правила."""
        delete(
            self.autoshutdown_v1_url,
            body='',
            headers={'content-type': 'application/json; charset=utf-8'},
        )
        result = runner.invoke(cli, ['js', 'autoshutdown', 'delete', '00000000-0000-4000-8000-000000000000'])

        assert result.exit_code == 0
