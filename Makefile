UV ?= uv

.PHONY: all build install run clean lint test

all: build

build:
	$(UV) build

install:
	$(UV) venv
	$(UV) pip install -e . flake8 mypy pytest

run:
	$(UV) run pacodexion

test:
	$(UV) run pytest

lint:
	$(UV) run flake8 src tests
	$(UV) run mypy --strict src tests

clean:
	find src -type d -name "__pycache__" -exec rm -r {} +
	find src -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf traces
	rm -rf .venv
	rm -rf .pytest_cache
