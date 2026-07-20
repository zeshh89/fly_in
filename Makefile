VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

APP=main.py

.PHONY: all venv install run run-map test clean reset

all: venv install

venv:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)

install: venv
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install --no-cache-dir --no-deps pygame
	$(PIP) install flake8 mypy

lint:
	$(VENV)/bin/flake8 . --exclude=.venv,.git,__pycache__,.mypy_cache
	$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs


run:
	@echo "Running default simulation..."
	$(PYTHON) $(APP)

run-map:
	@echo "Running simulation with map: $(MAP)"
	$(PYTHON) $(APP) $(MAP)

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest -q

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

reset:
	rm -rf $(VENV)
