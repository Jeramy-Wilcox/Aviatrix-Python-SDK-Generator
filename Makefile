SHELL            := /bin/bash
.DEFAULT_GOAL    := help
ROOT_PATH		 := .
APP_PATH		 := $(ROOT_PATH)/application
VENV_PATH		 := $(ROOT_PATH)/venv
DOCS_DIR         := $(ROOT_PATH)/docs

# If you want a specific Python interpreter define it as an envvar
#export PYTHON_ENV=python3.8
ifdef PYTHON_ENV
	PYTHON := $(PYTHON_ENV)
else
	PYTHON := python3
endif


define PRINT_HELP_PYSCRIPT
import re, sys

class Style:
    BOLD = '\033[1m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    ENDC = '\033[0m'

print(f"{Style.BOLD}Please use `make <target>` where <target> is one of{Style.ENDC}")
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if line.startswith("# -------"):
		print(f"\n{Style.RED}{line}{Style.ENDC}")
	if match:
		target, help_msg = match.groups()
		if not target.startswith('--'):
			print(f"{Style.BOLD+Style.GREEN}{target:20}{Style.ENDC} - {help_msg}")
endef

export PRINT_HELP_PYSCRIPT
# See: https://docs.python.org/3/using/cmdline.html#envvar-PYTHONWARNINGS
export PYTHONWARNINGS=ignore

#################################### Functions ###########################################
# Function to check if package is installed else install it.
define install_pip_pkg_if_not_exist
	@for pkg in ${1} ${2} ${3}; do \
		if ! command -v "$${pkg}" >/dev/null 2>&1; then \
			echo "installing $${pkg}"; \
			$(PYTHON) -m pip install $${pkg}; \
		fi;\
	done
endef

# Function to create python virtualenv if it doesn't exist
define create-venv
        $(call install_pip_pkg_if_not_exist,virtualenv)

        @if [ ! -d "venv" ]; then \
                $(PYTHON) -m virtualenv "venv" -p python3.8 -q; \
                venv/bin/python -m pip install -qU pip; \
                venv/bin/python -m pip install -r requirements-dev.txt; \
                echo "\"venv\": Created successfully!"; \
        fi;
        @echo "Source virtual environment before tinkering"
        @echo -e "\tRun: \`source venv/bin/activate\`"
endef

########################################### END ##########################################

help:
	@$(PYTHON) -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

# ------------------------------------ Installations -------------------------------------

.PHONY: install
install:  ## Check if package exist, if not install the package
# 	@$(PYTHON) -c "import $(PACKAGE_NAME)" >/dev/null 2>&1 ||
	$(PYTHON) -m pip install .;

venv:  ## Create virtualenv environment on local directory.
	@$(create-venv)

# ------------------------------------Code Style  ----------------------------------------

lint:  ## Check style with `flake8` and `mypy`
	python -m isort .
	python -m black .
	python -m flake8 .
	python -m pydocstyle .
	python -m mypy --strict .

darglint: ## Doc string argument linter
	find ifm_aviatrix -type f \( -iname "*.py" \) | xargs darglint -x

# ------------------------------------Clean Up  ------------------------------------------
.PHONY: clean
clean: clean_build clean_pyc clean_test ## Remove all build, test, coverage and Python artefacts

clean_build:  ## Remove build artefacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +
	find . -name '*.xml' -exec rm -fr {} +

clean_pyc:  ## Remove Python file artefacts
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '*.pyo' -exec rm -rf {} +
	find . -name '*~' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean_test:  ## Remove test and coverage artefacts
	rm -fr .tox/
	rm -fr .pytest_cache
	rm -fr .mypy_cache
	rm -fr .coverage
	rm -fr .pytest_cache
	rm -fr cov.xml

# ------------------------------------ Tests ---------------------------------------------

test:  ## Run tests quickly
	$(call install_pip_pkg_if_not_exist,pytest)
	$(PYTHON) -m pytest tests/

# ------------------------------------ Test Coverage --------------------------------------

cov:  ## Check code coverage quickly with pytest
	pytest \
	--cov=generator \
	--cov-report html \
	--cov-report term \
	--cov-report xml:cov.xml \
	tests/
