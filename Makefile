UV ?= uv

.PHONY: all build install run clean lint

all: build

build:
	$(UV) build

install:
	$(UV) venv
	$(UV) pip install -e . flake8 mypy

run:
	$(UV) run pacodexion

lint:
	$(UV) run flake8 src
	$(UV) run mypy --strict src

clean:
	find src -type d -name "__pycache__" -exec rm -r {} +
	find src -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf traces
	rm -rf .venv
	rm -rf .pytest_cache
