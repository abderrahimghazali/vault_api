# Makefile for Vault API

# Variables
PYTHON := python3
PIP := pip
VENV := venv
VENV_BIN := $(VENV)/bin
PYTHON_VENV := $(VENV_BIN)/python
PIP_VENV := $(VENV_BIN)/pip
UVICORN := $(VENV_BIN)/uvicorn
HOST := 0.0.0.0
PORT := 8000
WORKERS := 1
APP := app.main:app

# Colors for output
GREEN := \033[0;32m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help install setup start stop restart logs test clean db-status db-shell api-shell check-env

# Default target
help:
	@echo "$(BLUE)Vault API Makefile Commands:$(NC)"
	@echo "$(GREEN)Setup:$(NC)"
	@echo "  make install    - Create venv and install dependencies"
	@echo "  make setup      - Complete setup (install + create .env)"
	@echo ""
	@echo "$(GREEN)Server:$(NC)"
	@echo "  make start      - Start API server (development mode)"
	@echo "  make start-prod - Start API server (production mode)"
	@echo "  make stop       - Stop API server"
	@echo "  make restart    - Restart API server"
	@echo "  make logs       - Show API logs"
	@echo ""
	@echo "$(GREEN)Database:$(NC)"
	@echo "  make db-status  - Check database connection"
	@echo "  make db-shell   - Open PostgreSQL shell"
	@echo "  make db-migrate - Run database migrations"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
	@echo "  make api-shell  - Open Python shell with app context"
	@echo "  make clean      - Clean up generated files"

# Install dependencies
install:
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@$(PIP_VENV) install --upgrade pip
	@$(PIP_VENV) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed!$(NC)"

# Complete setup
setup: install
	@echo "$(BLUE)Setting up environment...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(BLUE)Creating .env file...$(NC)"; \
		POSTGRES_PORT=$$(ddev describe | grep -oP 'Host: 127.0.0.1:([0-9]+) \(PostgreSQL\)' | grep -oP '127.0.0.1:\K[0-9]+'); \
		ENCRYPTION_KEY=$$($(PYTHON) -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"); \
		echo "OPENAI_API_KEY=your-openai-api-key-here" > .env; \
		echo "DATABASE_URL=postgresql://db:db@127.0.0.1:$$POSTGRES_PORT/vault_db" >> .env; \
		echo "ENCRYPTION_KEY=$$ENCRYPTION_KEY" >> .env; \
		echo "API_VERSION=v1" >> .env; \
		echo "DEBUG=True" >> .env; \
		echo "$(GREEN)✓ .env file created! Please update OPENAI_API_KEY$(NC)"; \
	else \
		echo "$(GREEN)✓ .env file already exists$(NC)"; \
	fi

# Start API server (development)
start: check-env
	@echo "$(BLUE)Starting Vault API server (development)...$(NC)"
	@$(UVICORN) $(APP) --reload --host $(HOST) --port $(PORT)

# Start API server (production)
start-prod: check-env
	@echo "$(BLUE)Starting Vault API server (production)...$(NC)"
	@$(UVICORN) $(APP) --host $(HOST) --port $(PORT) --workers $(WORKERS)

# Start API server in background
start-bg: check-env
	@echo "$(BLUE)Starting Vault API server in background...$(NC)"
	@nohup $(UVICORN) $(APP) --host $(HOST) --port $(PORT) > vault-api.log 2>&1 & echo $$! > vault-api.pid
	@echo "$(GREEN)✓ API server started! PID: $$(cat vault-api.pid)$(NC)"

# Stop API server
stop:
	@if [ -f vault-api.pid ]; then \
		echo "$(BLUE)Stopping Vault API server...$(NC)"; \
		kill $$(cat vault-api.pid) 2>/dev/null || true; \
		rm -f vault-api.pid; \
		echo "$(GREEN)✓ API server stopped$(NC)"; \
	else \
		echo "$(RED)No running server found$(NC)"; \
		pkill -f "uvicorn $(APP)" 2>/dev/null || true; \
	fi

# Restart API server
restart: stop start

# Show logs
logs:
	@if [ -f vault-api.log ]; then \
		tail -f vault-api.log; \
	else \
		echo "$(RED)No log file found. Use 'make start-bg' to run in background with logs$(NC)"; \
	fi

# Check environment
check-env:
	@if [ ! -d $(VENV) ]; then \
		echo "$(RED)Virtual environment not found. Run 'make install' first$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f .env ]; then \
		echo "$(RED).env file not found. Run 'make setup' first$(NC)"; \
		exit 1; \
	fi

# Database status
db-status:
	@echo "$(BLUE)Checking database connection...$(NC)"
	@ddev describe | grep PostgreSQL
	@$(PYTHON_VENV) -c "from app.db.connection import engine; \
		from sqlalchemy import text; \
		with engine.connect() as conn: \
			result = conn.execute(text('SELECT version()')); \
			print(f'$(GREEN)✓ Database connected!$(NC)'); \
			print(f'PostgreSQL version: {result.scalar()}')"

# Open database shell
db-shell:
	@echo "$(BLUE)Opening PostgreSQL shell...$(NC)"
	@ddev psql -U db -d vault_db

# Run database migrations
db-migrate: check-env
	@echo "$(BLUE)Running database migrations...$(NC)"
	@$(PYTHON_VENV) -c "from app.db.migrations import init_database, create_indexes; \
		init_database(); \
		create_indexes(); \
		print('$(GREEN)✓ Database migrations complete!$(NC)')"

# Run tests
test: check-env
	@echo "$(BLUE)Running tests...$(NC)"
	@$(VENV_BIN)/pytest tests/ -v

# Run linting
lint: check-env
	@echo "$(BLUE)Running linting...$(NC)"
	@$(VENV_BIN)/flake8 app/ --max-line-length=100 --ignore=E501,W503

# Format code
format: check-env
	@echo "$(BLUE)Formatting code...$(NC)"
	@$(VENV_BIN)/black app/
	@$(VENV_BIN)/isort app/

# Open Python shell with app context
api-shell: check-env
	@$(PYTHON_VENV) -i -c "from app.config import settings; \
		from app.db.connection import SessionLocal, engine; \
		from app.models.database import *; \
		from app.services.vault import vault_service; \
		from app.services.encryption import encryption_service; \
		from app.services.embedding import embedding_service; \
		db = SessionLocal(); \
		print('$(GREEN)Vault API Shell$(NC)'); \
		print('Available objects: settings, db, vault_service, encryption_service, embedding_service'); \
		print('Models: VaultItem');"

# Test API endpoints
test-api:
	@echo "$(BLUE)Testing API endpoints...$(NC)"
	@echo "$(GREEN)Health check:$(NC)"
	@curl -s http://localhost:$(PORT)/api/v1/health | python3 -m json.tool
	@echo "\n$(GREEN)Ready check:$(NC)"
	@curl -s http://localhost:$(PORT)/api/v1/health/ready | python3 -m json.tool
	@echo "\n$(GREEN)API docs available at:$(NC) http://localhost:$(PORT)/docs"

# Create a test item
test-create:
	@echo "$(BLUE)Creating test vault item...$(NC)"
	@curl -X POST "http://localhost:$(PORT)/api/v1/vault/items" \
		-H "Content-Type: application/json" \
		-d '{"name": "Test Item", "data": "This is a test secret", "metadata": {"type": "test"}}' \
		| python3 -m json.tool

# Clean up
clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@rm -f vault-api.pid
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# Full cleanup (including venv)
clean-all: clean
	@echo "$(RED)Removing virtual environment...$(NC)"
	@rm -rf $(VENV)
	@echo "$(GREEN)✓ Full cleanup complete$(NC)"

# Show status
status:
	@echo "$(BLUE)Vault API Status:$(NC)"
	@if [ -f vault-api.pid ] && kill -0 $$(cat vault-api.pid) 2>/dev/null; then \
		echo "$(GREEN)✓ API Server: Running (PID: $$(cat vault-api.pid))$(NC)"; \
	else \
		echo "$(RED)✗ API Server: Not running$(NC)"; \
	fi
	@if ddev describe | grep -q "OK"; then \
		echo "$(GREEN)✓ DDEV: Running$(NC)"; \
	else \
		echo "$(RED)✗ DDEV: Not running$(NC)"; \
	fi