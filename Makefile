CI_PROJECT_DIR := $(or $(CI_PROJECT_DIR),$$(pwd))
WHL_DIR = dist
COVER = cover
DOCS = docs

##################################################################################

test:
	PYTHONPATH=$(CI_PROJECT_DIR) poetry run pytest -vvv ./tests/ \
		--cov=mls --cov=mls_core --cov-report=term-missing --cov-report=xml:${CI_PROJECT_DIR}/cover/coverage.xml \
		--junitxml=${CI_PROJECT_DIR}/cover/rspec.xml --cov-fail-under=87

test_report:
	PYTHONPATH=$(CI_PROJECT_DIR) poetry run pytest -vvv ./tests/ \
		--cov=mls --cov=mls_core --cov-report=term-missing --cov-report=html:${CI_PROJECT_DIR}/cover/html \
		--junitxml=${CI_PROJECT_DIR}/cover/rspec.xml --cov-fail-under=87

lint:
	@pre-commit run --all-files

check: lint test

version:
	@hatch version

build:
	@hatch build

clear:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf $(WHL_DIR)
	rm -rf $(COVER)
	rm -rf $(DOCS)

.PHONY: test clear coverage build verion
