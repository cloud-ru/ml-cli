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

all: $(MLS_COMMANDS)

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
	rm -f references__job-*.rst references__transfer-*.rst references__connector-*.rst
