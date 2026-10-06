.PHONY: install test lint demo

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests

demo:
	financial-analytics demo
