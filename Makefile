.PHONY: help install dev setup run run-worker test test-unit test-integration test-e2e test-cov typecheck lint lint-fix format format-check check clean migration migrate migrate-down migrate-history init-db seed docker-build docker-up docker-down docker-logs docs docs-serve shell version deps-tree


# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Multi-Agent System - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'



install: ## Install production dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	uv sync --no-dev

dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	uv sync

setup: dev ## Initial project setup
	@echo "$(BLUE)Setting up project...$(NC)"
	cp .env.example .env || true
	pre-commit install
	@echo "$(GREEN)Setup complete! Edit .env with your configuration.$(NC)"


run: ## Run the API server
	@echo "$(BLUE)Starting API server...$(NC)"
	uv run uvicorn multi_agent_system.api.app:app --reload --host 0.0.0.0 --port 8000

run-worker: ## Run Celery worker
	@echo "$(BLUE)Starting Celery worker...$(NC)"
	uv run celery -A multi_agent_system.tasks worker --loglevel=info

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	uv run pytest

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	uv run pytest tests/unit -v

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	uv run pytest tests/integration -v

test-e2e: ## Run end-to-end tests only
	@echo "$(BLUE)Running e2e tests...$(NC)"
	uv run pytest tests/e2e -v

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	uv run pytest --cov --cov-report=html --cov-report=term
	@echo "$(GREEN)Coverage report generated in htmlcov/index.html$(NC)"

typecheck: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(NC)"
	uv run mypy src/multi_agent_system

lint: ## Run linting with ruff
	@echo "$(BLUE)Running linter...$(NC)"
	uv run ruff check src/ tests/

lint-fix: ## Fix auto-fixable linting issues
	@echo "$(BLUE)Fixing linting issues...$(NC)"
	uv run ruff check --fix src/ tests/

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run ruff format src/ tests/

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(NC)"
	uv run ruff format --check src/ tests/

check: format-check lint typecheck test ## Run all quality checks

clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml
	@echo "$(GREEN)Cleanup complete!$(NC)"

migration: ## Create a new migration (use: make migration MSG="description")
	@echo "$(BLUE)Creating migration...$(NC)"
	uv run alembic revision --autogenerate -m "$(MSG)"

migrate: ## Apply database migrations
	@echo "$(BLUE)Applying migrations...$(NC)"
	uv run alembic upgrade head

migrate-down: ## Rollback last migration
	@echo "$(YELLOW)Rolling back migration...$(NC)"
	uv run alembic downgrade -1

migrate-history: ## Show migration history
	@echo "$(BLUE)Migration history:$(NC)"
	uv run alembic history

init-db: ## Initialize database
	@echo "$(BLUE)Initializing database...$(NC)"
	uv run python scripts/init_db.py

seed: ## Seed database with test data
	@echo "$(BLUE)Seeding database...$(NC)"
	uv run python scripts/seed_data.py

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t multi-agent-system:latest .

docker-up: ## Start all services with docker-compose
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose -f docker/docker-compose.yml up -d
	@echo "$(GREEN)Services started! API available at http://localhost:8000$(NC)"

docker-down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose -f docker/docker-compose.yml down

docker-logs: ## Show service logs
	docker-compose -f docker/docker-compose.yml logs -f

docs: ## Generate API documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	uv run mkdocs build

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation at http://127.0.0.1:8001$(NC)"
	uv run mkdocs serve -a 127.0.0.1:8001

shell: ## Open Python shell with project context
	uv run ipython

version: ## Show project version
	@echo "$(BLUE)Multi-Agent System$(NC)"
	@grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/Version: \1/'

deps-tree: ## Show dependency tree
	@echo "$(BLUE)Dependency tree:$(NC)"
	uv tree

.DEFAULT_GOAL := help