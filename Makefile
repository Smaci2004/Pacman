# Makefile used to manage the Pac-Man project.
# Available targets include install, run, debug, clean, lint and lint-strict.

PYTHON  := python3
VENV    := .venv
PIP     := $(VENV)/bin/pip
PY      := $(VENV)/bin/python
CONFIG  := config.json
WHEEL   := utils/mazegenerator-00001-py3-none-any.whl

# Directories excluded from static checks include the virtual environment
# and the provided A-Maze-ing package. These contain external code.
# The mypy expression matches complete directory names to avoid excluding
# project files such as maze/utils.py.
FLAKE_EXCLUDE := $(VENV),utils
MYPY_EXCLUDE  := (^|/)($(subst .,\.,$(VENV))|utils)/

.PHONY: install run debug clean lint lint-strict venv help

help:
	@echo "Targets: install run debug clean lint lint-strict"

# Set up the Python environment when it is not already available.
$(VENV):
	$(PYTHON) -m venv $(VENV)

venv: $(VENV)

# Install the project package and the dependencies listed in requirements.txt.
install: venv
	$(PIP) install --upgrade pip
	$(PIP) install $(WHEEL)
	$(PIP) install -r requirements.txt

# Start Pac-Man using the configured default settings.
run:
	$(PY) pac-man.py $(CONFIG)

# Run the application through the standard Python debugger.
debug:
	$(PY) -m pdb pac-man.py $(CONFIG)

# Delete generated caches and temporary build directories.
# The virtual environment is preserved and can be removed separately.
clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache .pytest_cache
	rm -rf build dist
	find . -name '*.pyc' -not -path './$(VENV)/*' -delete

# Run the required flake8 and mypy checks with the project settings.
lint:
	$(VENV)/bin/flake8 --exclude=$(FLAKE_EXCLUDE) .
	$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs --exclude '$(MYPY_EXCLUDE)'

# Perform a more restrictive version of the linting checks.
# Missing imports are ignored because the supplied maze package does not
# provide type information for mypy.
lint-strict:
	$(VENV)/bin/flake8 --exclude=$(FLAKE_EXCLUDE) .
	$(VENV)/bin/mypy . --strict --ignore-missing-imports \
		--exclude '$(MYPY_EXCLUDE)'
