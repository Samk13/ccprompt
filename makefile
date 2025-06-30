.PHONY: test format lint install ruff-check sync build clean help

sync:
	uv sync --group dev --all-extras

install:
	uv sync --group dev --all-extras

dev-install:
	uv sync --group dev --all-extras

build:
	uv build

run:
	uv run ccprompt --log_level DEBUG

test:
	uv run pytest

format:
	uv run ruff format . && uv run ruff check . --fix

lint-check:
	uv run ruff check .

lint-fix:
	uv run ruff check . --fix

change-log:
	# get the latest changes from the last tag for CHANGES.rst
	@git log $$(git describe --tags --abbrev=0)..HEAD --pretty=format:"%s"

help:
	@echo "Available commands:"
	@echo "  sync        - Install dependencies with uv"
	@echo "  install     - Alias for sync"
	@echo "  dev-install - Alias for sync (for compatibility)"
	@echo "  build       - Build distribution packages"
	@echo "  run         - Run ccprompt with debug logging"
	@echo "  test        - Run test suite with pytest"
	@echo "  format      - Format and fix code with ruff"
	@echo "  lint-check  - Check code style with ruff"
	@echo "  lint-fix    - Fix code style issues with ruff"
	@echo "  clean       - Remove build artifacts and cache"
	@echo "  change-log  - Show changes since last tag"
	@echo "  help        - Show this help message"

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete