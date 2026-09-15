# Run from the repository root with GNU Make and an activated Python 3.11 venv.
PYTHON ?= python
# Resolve before recipes change directory (also supports paths containing spaces).
PYTHON_EXE := $(shell $(PYTHON) -c "import sys; print(sys.executable)")
export PYTHONUTF8 := 1

.PHONY: help install install-dev run test lint format preprocess train
.DEFAULT_GOAL := help

help:
	@echo "install      Install runtime and training dependencies"
	@echo "install-dev  Install runtime dependencies and Ruff"
	@echo "run          Start the local Flask server via wsgi.py"
	@echo "test         Run existing diagnostic smoke checks (no assertion suite)"
	@echo "lint         Check Python lint and formatting"
	@echo "format       Format Python files without applying lint fixes"
	@echo "preprocess   Regenerate src/dataset_procesado.csv"
	@echo "train        Train and replace src/modelo_predictivo.pkl (close plot to finish)"

install:
	"$(PYTHON_EXE)" -m pip install -r requirements.txt

install-dev:
	"$(PYTHON_EXE)" -m pip install -r requirements-dev.txt

run:
	"$(PYTHON_EXE)" wsgi.py

test:
	@echo "Smoke checks only: inspect printed predictions; these scripts have no failure assertions."
	"$(PYTHON_EXE)" tests/test_fix.py
	"$(PYTHON_EXE)" tests/test_coordenadas_especificas.py
	cd src && "$(PYTHON_EXE)" ../tests/test_correccion.py

lint:
	"$(PYTHON_EXE)" -m ruff check .
	"$(PYTHON_EXE)" -m ruff format --check .

format:
	"$(PYTHON_EXE)" -m ruff format .

preprocess:
	cd src && "$(PYTHON_EXE)" procesar_dataset.py

train:
	cd src && "$(PYTHON_EXE)" Modelo.py
