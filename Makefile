PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python

.PHONY: venv setup test release-checks plan-matrix ci

venv:
	$(PYTHON) -m venv $(VENV)

setup: venv
	$(VENV_PYTHON) -m ensurepip --upgrade
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e .

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

release-checks:
	$(PYTHON) scripts/run_release_checks.py

plan-matrix:
	$(PYTHON) scripts/check_plan_matrix.py --protocol-dir protocol

ci:
	$(PYTHON) scripts/run_release_checks.py --plan-matrix
