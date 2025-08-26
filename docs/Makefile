# Установите переменные
PYTHON = python
SCRIPT = script.py
TEMPLATE = template.rst

# Определяем команды и их аргументы
MLS_COMMANDS = job transfer connector
MLS_JOB_COMMANDS = kill list logs pods regions restart status submit table types yaml
MLS_TRANSFER_COMMANDS = activate create deactivate delete get history list logs stop update
MLS_CONNECTOR_COMMANDS = activate create deactivate delete list sources update

# Генерируем цели для всех команд
.PHONY: all

all: $(MLS_COMMANDS) main
	$(PYTHON) $(SCRIPT) $(TEMPLATE) "mls configure --help" references__configure.rst
	$(PYTHON) $(SCRIPT) $(TEMPLATE) "mls job --help" references__job.rst
	$(PYTHON) $(SCRIPT) $(TEMPLATE) "mls transfer --help" references__transfer.rst
	$(PYTHON) $(SCRIPT) $(TEMPLATE) "mls connector --help" references__connector.rst

main:
	$(PYTHON) $(SCRIPT) $(TEMPLATE) "mls --help" references__common.rst

job: $(addprefix references__job-, $(addsuffix .rst, $(MLS_JOB_COMMANDS)))

transfer: $(addprefix references__transfer-, $(addsuffix .rst, $(MLS_TRANSFER_COMMANDS)))

connector: $(addprefix references__connector-, $(addsuffix .rst, $(MLS_CONNECTOR_COMMANDS)))

# Определяем цели для каждой команды
references__job-%.rst:
	$(PYTHON) $(SCRIPT) $(TEMPLATE) "mls job $* --help" $@

references__transfer-%.rst:
	$(PYTHON) $(SCRIPT) $(TEMPLATE) "mls transfer $* --help" $@

references__connector-%.rst:
	$(PYTHON) $(SCRIPT) $(TEMPLATE) "mls connector $* --help" $@

# Очистка всех сгенерированных файлов
clean:
	rm -f references__job-*.rst references__transfer-*.rst references__connector-*.rst mls.rst
	rm -f *.rst

#
# Для локального запуска
# make -f ./docs/Makefile local.test

export PYTHONPATH=$(pwd):$PYTHONPATH
LOCAL_SCRIPT = ./docs/script.py
LOCAL_TEMPLATE = ./docs/template.rst
MLS_LOCAL = ./mls/cli.py

local.test: $(addprefix local.job., $(MLS_JOB_COMMANDS)) $(addprefix local.transfer., $(MLS_TRANSFER_COMMANDS)) $(addprefix local.connector., $(MLS_CONNECTOR_COMMANDS))
	$(PYTHON) $(LOCAL_SCRIPT) $(LOCAL_TEMPLATE) "$(PYTHON) $(MLS_LOCAL) configure --help" configure.rst
	$(PYTHON) $(LOCAL_SCRIPT) $(LOCAL_TEMPLATE) "$(PYTHON) $(MLS_LOCAL) --help" main.rst

local.job.%:
	$(PYTHON) $(LOCAL_SCRIPT) $(LOCAL_TEMPLATE) "$(PYTHON) $(MLS_LOCAL) job $* --help" job.$*.rst

local.transfer.%:
	$(PYTHON) $(LOCAL_SCRIPT) $(LOCAL_TEMPLATE) "$(PYTHON) $(MLS_LOCAL) transfer $* --help" transfer.$*.rst

local.connector.%:
	$(PYTHON) $(LOCAL_SCRIPT) $(LOCAL_TEMPLATE) "$(PYTHON) $(MLS_LOCAL) connector $* --help" connector.$*.rst
