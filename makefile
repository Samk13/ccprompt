.PHONY: test format lint install ruff-check

install:
	pip install .[dev]

dev-install:
	pip install -e .

run:
	ccprompt --log_level DEBUG

test:
	python -m unittest discover -s tests

format:
	ruff format . && ruff check . --fix

lint-check:
	ruff check .

lint-fix:
	ruff check . --fix