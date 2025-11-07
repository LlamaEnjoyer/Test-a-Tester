.PHONY: help format lint check test clean install

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make format     - Format code with black and isort"
	@echo "  make lint       - Run all linters (flake8, mypy, pylint)"
	@echo "  make check      - Check formatting without making changes"
	@echo "  make test       - Run all tests"
	@echo "  make clean      - Remove Python cache files"
	@echo "  make all        - Format, lint, and test"

install:
	pip install -r requirements.txt

format:
	@echo "Running isort..."
	isort .
	@echo "Running black..."
	black .
	@echo "✅ Code formatting complete!"

lint:
	@echo "Running flake8..."
	flake8 .
	@echo "Running mypy..."
	mypy app.py
	@echo "✅ Linting complete!"

check:
	@echo "Checking isort..."
	isort --check-only .
	@echo "Checking black..."
	black --check .
	@echo "✅ Format check complete!"

pylint:
	@echo "Running pylint..."
	pylint app.py

test:
	@echo "Running tests..."
	@for test_file in tests/test_*.py; do \
		if [ -f "$$test_file" ]; then \
			echo "Running $$(basename $$test_file)..."; \
			python "$$test_file" || exit 1; \
			echo ""; \
		fi \
	done
	@echo "✅ All tests passed!"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@echo "✅ Cleaned cache files!"

all: format lint test
	@echo "✅ All checks passed!"
