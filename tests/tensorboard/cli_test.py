"""Интеграционные тесты для CLI команд TensorBoards MLS."""
import json
import re
from urllib.parse import parse_qs
from urllib.parse import urlparse

import pytest
import responses
import yaml  # type: ignore

from mls.cli import cli
from tests.tensorboard.data import ASYNC_RESULT
from tests.tensorboard.data import CONFIG_RESPONSE
from tests.tensorboard.data import CREATE_TENSORBOARD_PAYLOAD
from tests.tensorboard.data import TENSORBOARD_DETAIL
from tests.tensorboard.data import TENSORBOARD_LIST


def normalize_help(output: str) -> str:
    """Упрощает проверку help-output без привязки к переносам терминала."""
    return ' '.join(output.split())


class TestTensorboardCli:
    """Тестовый класс для CLI команд TensorBoards."""

    tensorboard_uuid = '11111111-1111-4111-8111-111111111111'
    list_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/tensorboards/v2/tensorboards')
    create_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/tensorboards/v2/[^/\s]+/tensorboard')
    get_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/tensorboards/v2/tensorboard/[^/\s]+')
    pause_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/tensorboards/v2/tensorboard/[^/\s]+/pause')
    delete_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/tensorboards/v2/tensorboard/[^/\s]+')
    modify_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/tensorboards/v2/tensorboard/[^/\s]+/modify')
    resume_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/tensorboards/v2/[^/\s]+/tensorboard/[^/\s]+/resume')
    config_url = re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/configs\?cluster_type=MT')

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_config_uses_public_api_configs_mt(self, runner):
        """Команда TensorBoard config получает регионы, instance types и образы через Public API /configs."""
        responses.get(self.config_url, json=CONFIG_RESPONSE)
        expected = json.dumps(CONFIG_RESPONSE, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['tensorboard', 'config'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_config_accepts_workspace_id_argument(self, runner):
        """Команда TensorBoard config может переопределить x-workspace-id из аргумента."""
        workspace_id = '11111111-1111-4111-8111-111111111111'
        responses.get(self.config_url, json=CONFIG_RESPONSE)

        result = runner.invoke(cli, ['tensorboard', 'config', workspace_id])

        assert result.exit_code == 0
        assert responses.calls[-1].request.headers['x-workspace-id'] == workspace_id

    def test_tensorboard_help_texts_are_polished(self, runner):
        """Справка TensorBoard содержит согласованные описания без опечаток."""
        config_help = runner.invoke(cli, ['tensorboard', 'config', '--help'])
        get_help = runner.invoke(cli, ['tensorboard', 'get', '--help'])

        assert config_help.exit_code == 0
        assert get_help.exit_code == 0
        normalized_config_help = normalize_help(config_help.output)
        normalized_get_help = normalize_help(get_help.output)
        assert 'Отображает информацию о доступных регионах, инстанс типах и образах для TensorBoard.' in normalized_config_help
        assert 'информации об инстансе TensorBoard' in normalized_get_help
        assert 'инфомации' not in normalized_get_help

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_list_json(self, runner):
        """Тест команды списка TensorBoards с выводом в формате JSON."""
        responses.get(self.list_url, json=TENSORBOARD_LIST)
        expected = json.dumps(TENSORBOARD_LIST, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['tensorboard', 'list'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_list_query_params(self, runner):
        """Тест query-параметров команды list."""
        responses.get(self.list_url, json=TENSORBOARD_LIST)

        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'list',
                '--order_by',
                'name',
                '--desc',
                '--limit',
                '10',
                '--offset',
                '5',
                '--search',
                'tb',
                '--status',
                'Running,Paused',
            ],
        )

        assert result.exit_code == 0
        query = parse_qs(urlparse(responses.calls[-1].request.url).query)
        assert query == {
            'order_by': ['name'],
            'desc': ['True'],
            'limit': ['10'],
            'offset': ['5'],
            'search': ['tb'],
            'status': ['Running,Paused'],
        }

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_pause_uses_tensorboards_namespace(self, runner):
        """Тест команды pause TensorBoard через tensorboards namespace."""
        responses.post(self.pause_url, json=TENSORBOARD_DETAIL)
        expected = json.dumps(TENSORBOARD_DETAIL, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['tensorboard', 'pause', self.tensorboard_uuid])

        assert result.exit_code == 0
        assert result.output == expected
        assert responses.calls[-1].request.method == 'POST'
        assert '/tensorboards/v2/tensorboard/' in responses.calls[-1].request.url
        assert responses.calls[-1].request.body is None

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_get_uses_tensorboards_namespace(self, runner):
        """Тест команды получения TensorBoard через tensorboards namespace."""
        responses.get(self.get_url, json=TENSORBOARD_DETAIL)
        expected = json.dumps(TENSORBOARD_DETAIL, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['tensorboard', 'get', self.tensorboard_uuid])

        assert result.exit_code == 0
        assert result.output == expected
        assert responses.calls[-1].request.method == 'GET'
        assert responses.calls[-1].request.url.endswith(f'/tensorboards/v2/tensorboard/{self.tensorboard_uuid}')

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_delete_uses_tensorboards_namespace(self, runner):
        """Тест команды delete TensorBoard через tensorboards namespace."""
        responses.delete(self.delete_url, json=ASYNC_RESULT)
        expected = json.dumps(ASYNC_RESULT, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['tensorboard', 'delete', self.tensorboard_uuid])

        assert result.exit_code == 0
        assert result.output == expected
        assert responses.calls[-1].request.method == 'DELETE'
        assert responses.calls[-1].request.url.endswith(
            f'/tensorboards/v2/tensorboard/{self.tensorboard_uuid}',
        )

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_pause_api_error_is_printed(self, runner):
        """Тест вывода ошибки public-api для команды pause."""
        error = {
            'code': 409,
            'message': 'Process is already being executed',
        }
        responses.post(self.pause_url, json=error, status=409)
        expected = json.dumps(error, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['tensorboard', 'pause', self.tensorboard_uuid])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_resume_payload_and_tensorboards_namespace(self, runner):
        """Тест payload команды resume TensorBoard."""
        responses.post(self.resume_url, json=TENSORBOARD_DETAIL)
        expected = json.dumps(TENSORBOARD_DETAIL, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'resume',
                self.tensorboard_uuid,
                '--namespace',
                'default',
                '--region',
                'SR008',
                '--instance-type',
                'a100.1gpu.40',
            ],
        )

        assert result.exit_code == 0
        assert result.output == expected
        assert responses.calls[-1].request.method == 'POST'
        assert (
            f'/tensorboards/v2/default/tensorboard/{self.tensorboard_uuid}/resume'
            in responses.calls[-1].request.url
        )
        assert json.loads(responses.calls[-1].request.body) == {
            'region': 'SR008',
            'instance_type': 'a100.1gpu.40',
        }

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_resume_requires_instance_type_without_config(self, runner):
        """Resume TensorBoard без --config требует явный --instance-type."""
        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'resume',
                self.tensorboard_uuid,
                '--namespace',
                'default',
            ],
        )

        assert result.exit_code == 2
        assert '--instance-type' in result.output

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_create_uses_profile_region_when_cli_region_omitted(self, runner):
        """Create TensorBoard берёт region из профиля, если --region не передан."""
        responses.post(self.create_url, json=ASYNC_RESULT)

        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'create',
                '--namespace',
                'default',
                '--name',
                'tb-cli',
                '--image-name',
                'cr.ai.cloud.ru/aicloud-tensorboard/tensorboard-server',
                '--image-tag',
                'latest',
                '--image-type',
                'datahub',
                '--instance-type',
                'free.0gpu',
                '--logdir',
                '/home/jovyan/logs',
            ],
        )

        assert result.exit_code == 0
        assert json.loads(responses.calls[-1].request.body)['region'] == 'test_region'

    def test_tensorboard_yaml_prints_manifest_contract(self, runner):
        """Команда tensorboard yaml печатает пример namespace + tensorboard."""
        result = runner.invoke(cli, ['tensorboard', 'yaml'])

        assert result.exit_code == 0
        assert 'namespace:' in result.output
        assert 'tensorboard:' in result.output
        assert 'logdir:' in result.output

    def test_tensorboard_yaml_resume_prints_manifest_contract(self, runner):
        """Команда tensorboard yaml --resume печатает пример namespace + resume."""
        result = runner.invoke(cli, ['tensorboard', 'yaml', '--resume'])

        assert result.exit_code == 0
        assert 'namespace:' in result.output
        assert 'resume:' in result.output
        assert 'instance_type:' in result.output

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_create_from_hyphen_options_sends_full_payload(self, runner):
        """Тест передачи create через CLI-опции в стиле Jupyter Server."""
        s3_buckets = [
            {'bucket_name': 'bucket-a', 'access_rule': 'ro'},
            {'bucket_name': 'bucket-b', 'access_rule': 'rw'},
        ]
        s3_credentials = {
            's3_credentials_source': 'iam-product-sa',
            's3_tenant_id': 'tenant-a',
        }
        responses.post(self.create_url, json=ASYNC_RESULT)

        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'create',
                '--namespace',
                'default',
                '--name',
                'tb-cli',
                '--image-name',
                'cr.ai.cloud.ru/aicloud-tensorboard/tensorboard-server',
                '--image-tag',
                'latest',
                '--image-type',
                'datahub',
                '--instance-type',
                'a100.1gpu.40',
                '--region',
                'SR008',
                '--allocation-name',
                'allocation-a',
                '--queue-name',
                'queue-a',
                '--description',
                'created from cli',
                '--pause-at',
                '45 * * * *',
                '--postponed-pause-enabled',
                '--logdir',
                '/home/jovyan/logs',
                '--logdir',
                '/home/jovyan/test',
                '--tensorboard-params',
                '{"--port":"6006"}',
                '--s3-buckets-json',
                json.dumps(s3_buckets, separators=(',', ':')),
                '--s3-credentials-json',
                json.dumps(s3_credentials, separators=(',', ':')),
            ],
        )

        assert result.exit_code == 0
        assert json.loads(responses.calls[-1].request.body) == CREATE_TENSORBOARD_PAYLOAD

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_create_from_cli_collects_multiple_logdirs(self, runner):
        """Повторяемый --logdir собирается в список строк."""
        responses.post(self.create_url, json=ASYNC_RESULT)

        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'create',
                '--namespace',
                'default',
                '--name',
                'tb-cli',
                '--image-name',
                'cr.ai.cloud.ru/aicloud-tensorboard/tensorboard-server',
                '--image-tag',
                'latest',
                '--image-type',
                'datahub',
                '--instance-type',
                'a100.1gpu.40',
                '--logdir',
                '/home/jovyan/logs/train',
                '--logdir',
                '/home/jovyan/logs/eval',
                '--tensorboard-params',
                '{"--port":"6006"}',
            ],
        )

        assert result.exit_code == 0
        body = json.loads(responses.calls[-1].request.body)
        assert body['logdir'] == [
            '/home/jovyan/logs/train',
            '/home/jovyan/logs/eval',
        ]
        assert body['tensorboard_params'] == {'--port': '6006'}

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_create_rejects_tensorboard_params_with_non_string_values(self, runner):
        """tensorboard_params из CLI соответствует backend dict[str, str]."""
        responses.post(self.create_url, json=ASYNC_RESULT)

        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'create',
                '--namespace',
                'default',
                '--name',
                'tb-cli',
                '--image-name',
                'cr.ai.cloud.ru/aicloud-tensorboard/tensorboard-server',
                '--image-tag',
                'latest',
                '--image-type',
                'datahub',
                '--instance-type',
                'a100.1gpu.40',
                '--logdir',
                '/home/jovyan/logs',
                '--tensorboard-params',
                '{"--port":6006}',
            ],
        )

        assert result.exit_code == 2
        assert 'tensorboard_params' in result.output
        assert not any('/tensorboards/v2/' in call.request.url for call in responses.calls)

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_create_config_allows_cli_override(self, runner, tmp_path):
        """С --config явно переданные CLI-опции create переопределяют YAML."""
        config_path = tmp_path / 'create-tensorboard.yaml'
        config_payload = {
            **CREATE_TENSORBOARD_PAYLOAD,
            'name': 'tb-yaml',
            'image': {
                **CREATE_TENSORBOARD_PAYLOAD['image'],
                'tag': 'config-tag',
            },
            'region': 'SR006',
            'postponed_pause_enabled': True,
            's3_credentials': {
                's3_credentials_source': 'secret-manager',
                'secret_manager_secret_id': 'secret-from-config',
                's3_tenant_id': 'tenant-from-config',
            },
        }
        config_path.write_text(
            yaml.safe_dump(
                {
                    'namespace': 'ns-from-file',
                    'tensorboard': config_payload,
                },
                allow_unicode=True,
            ),
            encoding='utf-8',
        )
        responses.post(self.create_url, json=ASYNC_RESULT)

        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'create',
                '--config',
                str(config_path),
                '--namespace',
                'ns-from-cli',
                '--name',
                'tb-cli',
                '--instance-type',
                'free.0gpu',
            ],
        )

        assert result.exit_code == 0
        assert '/tensorboards/v2/ns-from-cli/tensorboard' in responses.calls[-1].request.url
        body = json.loads(responses.calls[-1].request.body)
        assert body['name'] == 'tb-cli'
        assert body['instance_type'] == 'free.0gpu'
        assert body['image']['tag'] == 'config-tag'

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_create_accepts_generated_sample_config(self, runner):
        """Сгенерированный sample TensorBoard create принимается через --config."""
        responses.post(self.create_url, json=ASYNC_RESULT)

        result = runner.invoke(
            cli,
            ['tensorboard', 'create', '--config', './samples/template.tensorboard.create.yaml'],
        )

        assert result.exit_code == 0
        assert '/tensorboards/v2/default/tensorboard' in responses.calls[-1].request.url
        assert json.loads(responses.calls[-1].request.body) == {
            'name': 'my-tensorboard',
            'image': {
                'name': 'cr.ai.cloud.ru/aicloud-tensorboard/tensorboard-server',
                'tag': 'latest',
                'type': 'datahub',
            },
            'instance_type': 'free.0gpu',
            'logdir': ['/home/jovyan/logs'],
            'region': 'test_region',
            'postponed_pause_enabled': False,
            's3_buckets': [{'bucket_name': 'test', 'access_rule': 'ro'}],
            's3_credentials': {
                's3_credentials_source': 'iam-product-sa',
                's3_tenant_id': 'tenant_id',
            },
            'tensorboard_params': {'--port': '6006'},
        }

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_create_requires_payload_source(self, runner):
        """Тест обязательных параметров create без YAML."""
        result = runner.invoke(cli, ['tensorboard', 'create', '--namespace', 'default'])

        assert result.exit_code == 2
        assert '--name' in result.output

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_create_missing_required_fields_from_config(self, runner, tmp_path):
        """Тест обязательных create-полей из YAML-манифеста."""
        config_path = tmp_path / 'create-tensorboard.yaml'
        config_path.write_text(
            yaml.safe_dump(
                {
                    'namespace': 'default',
                    'tensorboard': {
                        'name': 'tb-from-config',
                        'image': {
                            'name': 'cr.ai.cloud.ru/aicloud-tensorboard/tensorboard-server',
                            'tag': 'latest',
                            'type': 'datahub',
                        },
                    },
                },
                allow_unicode=True,
            ),
            encoding='utf-8',
        )

        result = runner.invoke(cli, ['tensorboard', 'create', '--config', str(config_path)])

        assert result.exit_code == 2
        assert 'instance_type' in result.output
        assert 'logdir' in result.output
        assert not any('/tensorboards/v2/' in call.request.url for call in responses.calls)

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_create_rejects_unknown_fields_from_config(self, runner, tmp_path):
        """Create config отклоняет поля вне OpenAPI schema."""
        config_path = tmp_path / 'create-tensorboard.yaml'
        payload = {
            **CREATE_TENSORBOARD_PAYLOAD,
            'unsupported_field': 'value',
        }
        config_path.write_text(
            yaml.safe_dump(
                {
                    'namespace': 'default',
                    'tensorboard': payload,
                },
                allow_unicode=True,
            ),
            encoding='utf-8',
        )
        responses.post(self.create_url, json=ASYNC_RESULT)

        result = runner.invoke(cli, ['tensorboard', 'create', '--config', str(config_path)])

        assert result.exit_code == 2
        assert 'Недопустимые поля TensorBoard create' in result.output
        assert 'unsupported_field' in result.output
        assert not any('/tensorboards/v2/' in call.request.url for call in responses.calls)

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_create_invalid_yaml_is_reported(self, runner, tmp_path):
        """Тест ошибки чтения невалидного YAML-конфига."""
        config_path = tmp_path / 'create-tensorboard.yaml'
        config_path.write_text('tensorboard: [', encoding='utf-8')

        result = runner.invoke(cli, ['tensorboard', 'create', '--config', str(config_path)])

        assert result.exit_code == 1
        assert 'Ошибка чтения YAML-файла' in result.output

    def test_create_rejects_invalid_s3_buckets_json(self, runner):
        """Тест отклонения невалидного JSON для s3_buckets."""
        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'create',
                '--namespace',
                'default',
                '--s3-buckets-json',
                '{"not": "array"}',
            ],
        )

        assert result.exit_code == 2
        assert 'Ожидался JSON-массив' in result.output

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_modify_does_not_accept_config_option(self, runner, tmp_path):
        """Команда TensorBoard modify не принимает YAML-config."""
        config_path = tmp_path / 'modify-tensorboard.yaml'
        config_path.write_text('description: updated tensorboard\n', encoding='utf-8')
        responses.post(self.modify_url, json=ASYNC_RESULT)

        result = runner.invoke(
            cli,
            ['tensorboard', 'modify', self.tensorboard_uuid, '--config', str(config_path)],
        )

        assert result.exit_code == 2
        assert 'No such option' in result.output
        assert '--config' in result.output
        assert not any('/modify' in call.request.url for call in responses.calls)

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_modify_from_options_uses_tensorboards_namespace(self, runner):
        """Тест команды modify TensorBoard через CLI-опции."""
        s3_buckets = [{'bucket_name': 'bucket-a', 'access_rule': 'ro'}]
        s3_credentials = {'s3_credentials_source': 'not-enabled'}
        payload = {
            'description': 'updated tensorboard',
            's3_buckets': s3_buckets,
            's3_credentials': s3_credentials,
        }
        responses.post(
            self.modify_url,
            match=[responses.matchers.json_params_matcher(payload)],
            json=ASYNC_RESULT,
        )
        expected = json.dumps(ASYNC_RESULT, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'modify',
                self.tensorboard_uuid,
                '--description',
                'updated tensorboard',
                '--s3-buckets-json',
                json.dumps(s3_buckets, separators=(',', ':')),
                '--s3-credentials-json',
                json.dumps(s3_credentials, separators=(',', ':')),
            ],
        )

        assert result.exit_code == 0
        assert result.output == expected
        assert responses.calls[-1].request.method == 'POST'
        assert responses.calls[-1].request.url.endswith(
            f'/tensorboards/v2/tensorboard/{self.tensorboard_uuid}/modify',
        )

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_modify_sends_only_explicit_cli_fields(self, runner):
        """Команда TensorBoard modify отправляет только явно заданные CLI-поля."""
        payload = {
            'description': 'updated tensorboard',
        }
        responses.post(
            self.modify_url,
            match=[responses.matchers.json_params_matcher(payload)],
            json=ASYNC_RESULT,
        )

        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'modify',
                self.tensorboard_uuid,
                '--description',
                'updated tensorboard',
            ],
        )

        assert result.exit_code == 0
        assert json.loads(responses.calls[-1].request.body) == payload

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_modify_requires_explicit_change(self, runner):
        """Команда TensorBoard modify требует хотя бы одно поле body payload."""
        result = runner.invoke(cli, ['tensorboard', 'modify', self.tensorboard_uuid])

        assert result.exit_code == 2
        assert 'Укажите хотя бы одно изменение' in result.output
        assert not any('/modify' in call.request.url for call in responses.calls)

    def test_pause_requires_valid_uuid(self, runner):
        """Тест валидации UUID для команды pause."""
        result = runner.invoke(cli, ['tensorboard', 'pause', 'not-a-uuid'])

        assert result.exit_code == 2
        assert 'Invalid value' in result.output

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_resume_requires_namespace(self, runner):
        """Тест обязательного namespace для команды resume."""
        result = runner.invoke(cli, ['tensorboard', 'resume', self.tensorboard_uuid])

        assert result.exit_code == 2
        assert '--namespace' in result.output

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_resume_from_yaml(self, runner, tmp_path):
        """Тест resume TensorBoard через YAML-конфиг."""
        config_path = tmp_path / 'resume-tensorboard.yaml'
        payload = {
            'region': 'SR006',
            'instance_type': 'a100.1gpu.40',
        }
        config_path.write_text(
            yaml.safe_dump(
                {
                    'namespace': 'ns-from-file',
                    'resume': payload,
                },
                allow_unicode=True,
            ),
            encoding='utf-8',
        )
        responses.post(self.resume_url, json=TENSORBOARD_DETAIL)

        result = runner.invoke(
            cli,
            ['tensorboard', 'resume', self.tensorboard_uuid, '--config', str(config_path)],
        )

        assert result.exit_code == 0
        assert (
            f'/tensorboards/v2/ns-from-file/tensorboard/{self.tensorboard_uuid}/resume'
            in responses.calls[-1].request.url
        )
        assert json.loads(responses.calls[-1].request.body) == payload

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_resume_accepts_generated_sample_config(self, runner):
        """Сгенерированный sample TensorBoard resume принимается через --config."""
        responses.post(self.resume_url, json=TENSORBOARD_DETAIL)

        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'resume',
                self.tensorboard_uuid,
                '--config',
                './samples/template.tensorboard.resume.yaml',
            ],
        )

        assert result.exit_code == 0
        assert (
            f'/tensorboards/v2/default/tensorboard/{self.tensorboard_uuid}/resume'
            in responses.calls[-1].request.url
        )
        assert json.loads(responses.calls[-1].request.body) == {
            'region': 'test_region',
            'instance_type': 'free.0gpu',
        }

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_resume_config_allows_cli_override(self, runner, tmp_path):
        """С --config явно переданные CLI-опции resume переопределяют YAML."""
        config_path = tmp_path / 'resume-tensorboard.yaml'
        config_payload = {
            'region': 'SR006',
            'instance_type': 'a100.1gpu.40',
        }
        config_path.write_text(
            yaml.safe_dump(
                {
                    'namespace': 'ns-from-file',
                    'resume': config_payload,
                },
                allow_unicode=True,
            ),
            encoding='utf-8',
        )
        responses.post(self.resume_url, json=TENSORBOARD_DETAIL)

        result = runner.invoke(
            cli,
            [
                'tensorboard',
                'resume',
                self.tensorboard_uuid,
                '--config',
                str(config_path),
                '--namespace',
                'ns-from-cli',
                '--region',
                'SR008',
                '--instance-type',
                'free.0gpu',
            ],
        )

        assert result.exit_code == 0
        assert (
            f'/tensorboards/v2/ns-from-cli/tensorboard/{self.tensorboard_uuid}/resume'
            in responses.calls[-1].request.url
        )
        assert json.loads(responses.calls[-1].request.body) == {
            'region': 'SR008',
            'instance_type': 'free.0gpu',
        }

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_list_text(self, runner):
        """Тест команды списка TensorBoards с текстовым выводом."""
        responses.get(self.list_url, json=TENSORBOARD_LIST)
        expected = str(TENSORBOARD_LIST) + '\n'

        result = runner.invoke(cli, ['tensorboard', 'list', '--output', 'text'])

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_create_config_requires_manifest_body(self, runner, tmp_path):
        """Create через --config требует manifest namespace + tensorboard."""
        config_path = tmp_path / 'create-tensorboard.yaml'
        payload = {
            **CREATE_TENSORBOARD_PAYLOAD,
            'name': 'tb-1',
            'instance_type': 'free.0gpu',
        }
        config_path.write_text(
            yaml.safe_dump({'namespace': 'default', **payload}, allow_unicode=True),
            encoding='utf-8',
        )
        responses.post(self.create_url, json=ASYNC_RESULT)

        result = runner.invoke(cli, ['tensorboard', 'create', '--config', str(config_path)])

        assert result.exit_code == 2
        assert 'В манифесте задайте объект tensorboard' in result.output
        assert not any('/tensorboards/v2/' in call.request.url for call in responses.calls)

    @pytest.mark.usefixtures('test_profile', 'mock_auth')
    @responses.activate
    def test_create_from_manifest_namespace_contract(self, runner, tmp_path):
        """Create через --config поддерживает manifest namespace + tensorboard."""
        config_path = tmp_path / 'create-tensorboard.yaml'
        payload = {
            **CREATE_TENSORBOARD_PAYLOAD,
            'name': 'tb-1',
            'instance_type': 'free.0gpu',
        }
        config_path.write_text(
            yaml.safe_dump(
                {
                    'namespace': 'ns-from-file',
                    'tensorboard': payload,
                },
                allow_unicode=True,
            ),
            encoding='utf-8',
        )
        responses.post(self.create_url, json=ASYNC_RESULT)
        expected = json.dumps(ASYNC_RESULT, indent=4, ensure_ascii=False) + '\n'

        result = runner.invoke(cli, ['tensorboard', 'create', '--config', str(config_path)])

        assert result.exit_code == 0
        assert result.output == expected
        assert '/tensorboards/v2/ns-from-file/tensorboard' in responses.calls[-1].request.url
        assert json.loads(responses.calls[-1].request.body) == payload
