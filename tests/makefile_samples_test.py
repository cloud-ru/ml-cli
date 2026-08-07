"""Тесты Makefile targets для sample YAML."""
from pathlib import Path


def test_makefile_has_grouped_notebook_service_sample_targets():
    """Makefile группирует create/resume samples по notebook-сервисам."""
    makefile = Path('Makefile').read_text(encoding='utf-8')

    assert 'jupyter_server_samples: $(JS_CREATE_SAMPLE) $(JS_RESUME_SAMPLE)' in makefile
    assert 'tensorboard_samples: $(TB_CREATE_SAMPLE) $(TB_RESUME_SAMPLE)' in makefile
    assert 'jupyter_server_samples tensorboard_samples' in makefile
    assert 'PYTHONPATH=$(CI_PROJECT_DIR) python -m mls.cli job types' in makefile


def test_jupyter_tensorboard_samples_keep_project_infographics():
    """Jupyter Server и TensorBoard samples используют стиль job samples."""
    makefile = Path('Makefile').read_text(encoding='utf-8')

    assert '# 🤝 Пример создания Jupyter Server:' in makefile
    assert '# 🤝 Пример возобновления Jupyter Server:' in makefile
    assert '# 🤝 Пример создания TensorBoard:' in makefile
    assert '# 🤝 Пример возобновления TensorBoard:' in makefile
    assert '# 📚 ⬇️ ⬇️ ⬇️' in makefile
