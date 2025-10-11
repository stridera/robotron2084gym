.PHONY: help install install-dev test lint format type-check clean run examples

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies using Poetry
	poetry install

install-dev:  ## Install dependencies including dev tools
	poetry install --with dev,examples

test:  ## Run tests with pytest
	poetry run pytest

lint:  ## Run linting with ruff
	poetry run ruff check robotron/ examples/

format:  ## Format code with black and ruff
	poetry run black robotron/ examples/
	poetry run ruff check --fix robotron/ examples/

type-check:  ## Run type checking with mypy
	poetry run mypy robotron/

clean:  ## Clean up temporary files
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

run:  ## Run the game (human playable)
	poetry run python main.py

run-headless:  ## Run quick test in headless mode
	poetry run python skeleton.py

examples:  ## Run all example scripts
	@echo "Running basic_usage..."
	poetry run python examples/basic_usage.py
	@echo "\nRunning reproducibility_demo..."
	poetry run python examples/reproducibility_demo.py
	@echo "\nRunning performance_comparison..."
	poetry run python examples/performance_comparison.py
	@echo "\nRunning custom_config..."
	poetry run python examples/custom_config.py
