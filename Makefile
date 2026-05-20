VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

APP=main.py

.PHONY: all venv install run run-map test clean reset

# -----------------------------
# SETUP
# -----------------------------
all: venv install

venv:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)

install: venv
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install pygame

# -----------------------------
# RUN
# -----------------------------
run:
	@echo "Running default simulation..."
	$(PYTHON) $(APP)

run-map:
	@echo "Running simulation with map: $(MAP)"
	$(PYTHON) $(APP) $(MAP)

# -----------------------------
# TESTS (opcional si luego usas pytest)
# -----------------------------
test:
	@echo "Running tests..."
	$(PYTHON) -m pytest -q

# -----------------------------
# CLEAN
# -----------------------------
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

reset:
	rm -rf $(VENV)