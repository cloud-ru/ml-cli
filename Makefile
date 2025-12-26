CI_PROJECT_DIR := $(or $(CI_PROJECT_DIR),$$(pwd))
WHL_DIR = dist
COVER = cover
DOCS = docs
SAMPLES = samples

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
	@command pip install ./dist/mls-*.whl --force-reinstall

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

TYPES = $(shell python ./mls/cli.py job types)

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


	@python ./mls/cli.py job yaml $* >> ./samples/template.$@

samples: directory $(addprefix , $(addsuffix .yaml, $(TYPES)))

.PHONY: test clear coverage build verion yaml directory

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
