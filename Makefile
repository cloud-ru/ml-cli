CI_PROJECT_DIR := $(or $(CI_PROJECT_DIR),$$(pwd))
WHL_DIR = dist
COVER = cover
DOCS = docs
SAMPLES = samples
JS_CREATE_SAMPLE = samples/template.jupyter_server_create.yaml
JS_RESUME_SAMPLE = samples/template.jupyter_server_resume.yaml
TB_CREATE_SAMPLE = samples/template.tensorboard.create.yaml
TB_RESUME_SAMPLE = samples/template.tensorboard.resume.yaml

##################################################################################

test: samples # are you unset MLS_PROFILE_DEFAULT ?
	PYTHONPATH=$(CI_PROJECT_DIR) poetry run pytest -vvv ./tests/ \
		--cov=mls --cov=mls_core --cov-report=term-missing --cov-report=xml:${CI_PROJECT_DIR}/cover/coverage.xml \
		--junitxml=${CI_PROJECT_DIR}/cover/rspec.xml --cov-fail-under=90 -s

test_report: samples
	PYTHONPATH=$(CI_PROJECT_DIR) poetry run pytest -vvv ./tests/ \
		--cov=mls --cov=mls_core --cov-report=term-missing --cov-report=html:${CI_PROJECT_DIR}/cover/html \
		--junitxml=${CI_PROJECT_DIR}/cover/rspec.xml --cov-fail-under=90

reinstall_package: build
	@command pip install -i https://pkg.sbercloud.tech/artifactory/api/pypi/proxies-pypi/simple ./dist/mls-*.whl --force-reinstall

lint: reinstall_package
	@pre-commit run --all-files

check: lint test

version:
	@hatch version

build:
	rm -rf ./dist/ || true
	echo "building ... "
	@hatch build
	@hatch version

clear:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf $(WHL_DIR)
	rm -rf $(COVER)
	rm -rf $(DOCS)

TYPES = $(shell PYTHONPATH=$(CI_PROJECT_DIR) python -m mls.cli job types)

directory:
	@mkdir -p samples

%.yaml : directory
	@echo "Сгенерированный набор примеров $@ from $*..."

	@echo "# 🤝 Пример запуска $*... задач через ☁️👔🔒 mls job submit --config ./$@" > ./samples/template.$@
	@echo "# 📚 health - 🚀Полностью опциональный параметр...   " >> ./samples/template.$@
	@echo "# 📚 policy - 🚀Полностью опциональный параметр...   " >> ./samples/template.$@
	@echo "# 📚 processes если не задан устанавливается в соответствии с gpu" >> ./samples/template.$@
	@echo "# 📚 Описание https://api.ai.cloud.ru/public/v2/redoc   " >> ./samples/template.$@
	@echo "# 📚 Образ: https://cloud.ru/docs/aicloud/mlspace/concepts/environments__basic-images-list__jobs.html " >> ./samples/template.$@
	@echo "# 📚 max_retry параметр применимый только к аллокациям " >> ./samples/template.$@
	@echo "# 📚 ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️" >> ./samples/template.$@
	@echo "# 📚 https://github.com/sbercloud-ai/aicloud-examples/tree/master/quick-start" >> ./samples/template.$@


	@env PYTHONPATH=$(CI_PROJECT_DIR) python ./mls/cli.py job yaml $* >> ./samples/template.$@
	@echo "Создан или обновлен файл ./samples/template.$@"

$(JS_CREATE_SAMPLE): directory
	@echo "# 🤝 Пример создания Jupyter Server: mls js create --config ./samples/template.jupyter_server_create.yaml" > $(JS_CREATE_SAMPLE)
	@echo "# 📚 --config задает базовый шаблон; явно переданные CLI-опции create переопределяют YAML. Region берётся из профиля, YAML или --region." >> $(JS_CREATE_SAMPLE)
	@echo "# 📚 Описание API: https://api.ai.cloud.ru/public/v2/redoc" >> $(JS_CREATE_SAMPLE)
	@echo "# 📚 ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️" >> $(JS_CREATE_SAMPLE)
	@env PYTHONPATH=$(CI_PROJECT_DIR) poetry run python ./mls/cli.py js yaml >> $(JS_CREATE_SAMPLE)
	@echo "Создан или обновлен файл $(JS_CREATE_SAMPLE)"

$(JS_RESUME_SAMPLE): directory
	@echo "# 🤝 Пример возобновления Jupyter Server: mls js resume --config ./samples/template.jupyter_server_resume.yaml" > $(JS_RESUME_SAMPLE)
	@echo "# 📚 --config задает базовый шаблон; явно переданные CLI-опции resume переопределяют YAML." >> $(JS_RESUME_SAMPLE)
	@echo "# 📚 UUID сервера передаётся аргументом команды. Регион берётся из профиля или из --region. Описание API: https://api.ai.cloud.ru/public/v2/redoc" >> $(JS_RESUME_SAMPLE)
	@echo "# 📚 ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️" >> $(JS_RESUME_SAMPLE)
	@env PYTHONPATH=$(CI_PROJECT_DIR) poetry run python ./mls/cli.py js yaml --resume >> $(JS_RESUME_SAMPLE)
	@echo "Создан или обновлен файл $(JS_RESUME_SAMPLE)"

$(TB_CREATE_SAMPLE): directory
	@echo "# 🤝 Пример создания TensorBoard: mls tensorboard create --config ./samples/template.tensorboard.create.yaml" > $(TB_CREATE_SAMPLE)
	@echo "# 📚 --config задает базовый шаблон; явно переданные CLI-опции create переопределяют YAML. Region берётся из профиля, YAML или --region." >> $(TB_CREATE_SAMPLE)
	@echo "# 📚 Описание API: https://api.ai.cloud.ru/public/v2/redoc" >> $(TB_CREATE_SAMPLE)
	@echo "# 📚 ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️" >> $(TB_CREATE_SAMPLE)
	@env PYTHONPATH=$(CI_PROJECT_DIR) poetry run python ./mls/cli.py tensorboard yaml >> $(TB_CREATE_SAMPLE)
	@echo "Создан или обновлен файл $(TB_CREATE_SAMPLE)"

$(TB_RESUME_SAMPLE): directory
	@echo "# 🤝 Пример возобновления TensorBoard: mls tensorboard resume --config ./samples/template.tensorboard.resume.yaml 00000000-0000-4000-8000-000000000000" > $(TB_RESUME_SAMPLE)
	@echo "# 📚 --config задает базовый шаблон; явно переданные CLI-опции resume переопределяют YAML. UUID передаётся аргументом команды." >> $(TB_RESUME_SAMPLE)
	@echo "# 📚 Описание API: https://api.ai.cloud.ru/public/v2/redoc" >> $(TB_RESUME_SAMPLE)
	@echo "# 📚 ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️" >> $(TB_RESUME_SAMPLE)
	@env PYTHONPATH=$(CI_PROJECT_DIR) poetry run python ./mls/cli.py tensorboard yaml --resume >> $(TB_RESUME_SAMPLE)
	@echo "Создан или обновлен файл $(TB_RESUME_SAMPLE)"

jupyter_server_samples: $(JS_CREATE_SAMPLE) $(JS_RESUME_SAMPLE)
	@echo "Jupyter Server samples готовы"

tensorboard_samples: $(TB_CREATE_SAMPLE) $(TB_RESUME_SAMPLE)
	@echo "TensorBoard samples готовы"

samples: directory $(addprefix , $(addsuffix .yaml, $(TYPES))) jupyter_server_samples tensorboard_samples

sample: samples
	@echo "Samples готовы в ./samples"

.PHONY: test clear coverage build verion yaml directory sample jupyter_server_samples tensorboard_samples

# -- оффлайн сборка --
clean_dist:
	@rm -rf ./dist || true
	mkdir ./dist
	mkdir -p ./dist/offline_packages

export_requirements: clean_dist
	poetry export --without-hashes --format=requirements.txt > ./dist/offline_packages/requirements.txt

download_packages: export_requirements
	pip download -r ./dist/offline_packages/requirements.txt -d ./dist/offline_packages

build_wheel:
	python -m build
	mv ./dist/*.whl ./dist/offline_packages/

generate_offline_makefile: build_wheel
	echo "all:\n\tpip install --no-index --find-links=. -r requirements.txt\n\tpip install ./*.whl" > ./dist/offline_packages/Makefile

tar_offline_packages: download_packages build_wheel generate_offline_makefile
	tar -czvf ./dist/installer.tar.gz -C ./dist/offline_packages .

# -- оффлайн установка --

un_tar_packages:
	tar -xzvf ./dist/installer.tar.gz -C ./dist/

offline_install:un_tar_packages
	make -C ./dist/offline_packages all
