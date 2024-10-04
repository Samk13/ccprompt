.PHONY: test format lint install ruff-check

install:
	pip install .[dev]

test:
	python -m unittest discover -s tests

format:
	ruff format .

lint-check:
	ruff check .

lint-fix:
	ruff check . --fix