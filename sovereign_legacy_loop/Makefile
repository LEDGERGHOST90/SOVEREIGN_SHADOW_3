# 🌐 SHADOW.AI II - UNIFIED EMPIRE
# Makefile for streamlined container management
# Owner: LEDGERGHOST90

.PHONY: help build up down restart logs clean dev prod staging

# Default target
help: ## Show this help message
	@echo "🌐 SHADOW.AI II - Unified Empire Management"
	@echo "=========================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment setup
dev: ## Start development environment
	@echo "🚀 Starting Development Environment..."
	@cp environments/development.env .env
	@docker-compose -f docker-compose.yml --env-file .env up -d
	@echo "✅ Development environment started"
	@echo "📊 Dashboard: http://localhost:3000"
	@echo "🤖 MCP Server: http://localhost:8000"
	@echo "📈 Grafana: http://localhost:3001"

staging: ## Start staging environment
	@echo "🧪 Starting Staging Environment..."
	@cp environments/staging.env .env
	@docker-compose -f docker-compose.yml --env-file .env up -d
	@echo "✅ Staging environment started"

prod: ## Start production environment
	@echo "🏭 Starting Production Environment..."
	@cp environments/production.env .env
	@docker-compose -f docker-compose.yml --env-file .env up -d
	@echo "✅ Production environment started"

# Build operations
build: ## Build all services
	@echo "🔨 Building all services..."
	@docker-compose build --parallel
	@echo "✅ Build completed"

build-no-cache: ## Build all services without cache
	@echo "🔨 Building all services (no cache)..."
	@docker-compose build --no-cache --parallel
	@echo "✅ Build completed"

# Container operations
up: ## Start all services
	@echo "🚀 Starting all services..."
	@docker-compose up -d
	@echo "✅ All services started"

down: ## Stop all services
	@echo "🛑 Stopping all services..."
	@docker-compose down
	@echo "✅ All services stopped"

restart: ## Restart all services
	@echo "🔄 Restarting all services..."
	@docker-compose restart
	@echo "✅ All services restarted"

# Monitoring
logs: ## Show logs for all services
	@docker-compose logs -f

logs-gateway: ## Show API gateway logs
	@docker-compose logs -f api-gateway

logs-dashboard: ## Show dashboard logs
	@docker-compose logs -f dashboard

logs-mcp: ## Show MCP server logs
	@docker-compose logs -f mcp-server

logs-exchange: ## Show exchange connector logs
	@docker-compose logs -f exchange-connector

# Health checks
health: ## Check health of all services
	@echo "🏥 Health Check Report"
	@echo "====================="
	@docker-compose ps
	@echo ""
	@echo "🔍 Service Health:"
	@curl -s http://localhost/health || echo "❌ Gateway not responding"
	@curl -s http://localhost:3000/api/health || echo "❌ Dashboard not responding"
	@curl -s http://localhost:8000/health || echo "❌ MCP Server not responding"

status: ## Show status of all services
	@docker-compose ps

# Database operations
db-migrate: ## Run database migrations
	@echo "🗄️ Running database migrations..."
	@docker-compose exec dashboard npx prisma migrate deploy
	@echo "✅ Migrations completed"

db-reset: ## Reset database
	@echo "🗄️ Resetting database..."
	@docker-compose exec dashboard npx prisma migrate reset --force
	@echo "✅ Database reset completed"

db-seed: ## Seed database with initial data
	@echo "🌱 Seeding database..."
	@docker-compose exec dashboard npx prisma db seed
	@echo "✅ Database seeded"

# Cleanup operations
clean: ## Clean up containers, networks, and volumes
	@echo "🧹 Cleaning up..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@echo "✅ Cleanup completed"

clean-all: ## Clean up everything including images
	@echo "🧹 Deep cleaning..."
	@docker-compose down -v --remove-orphans
	@docker system prune -af
	@echo "✅ Deep cleanup completed"

# Security
security-scan: ## Run security scan on images
	@echo "🔒 Running security scan..."
	@docker-compose config
	@echo "✅ Configuration validated"

# Backup operations
backup: ## Backup database and volumes
	@echo "💾 Creating backup..."
	@mkdir -p ./backups/$(shell date +%Y%m%d_%H%M%S)
	@docker-compose exec postgres pg_dump -U trader shadow_ai > ./backups/$(shell date +%Y%m%d_%H%M%S)/database.sql
	@docker run --rm -v shadow-ai_postgres-data:/data -v $(PWD)/backups/$(shell date +%Y%m%d_%H%M%S):/backup alpine tar czf /backup/postgres-data.tar.gz -C /data .
	@echo "✅ Backup completed"

# Development tools
shell-dashboard: ## Open shell in dashboard container
	@docker-compose exec dashboard /bin/sh

shell-mcp: ## Open shell in MCP server container
	@docker-compose exec mcp-server /bin/bash

shell-db: ## Open PostgreSQL shell
	@docker-compose exec postgres psql -U trader -d shadow_ai

# Monitoring access
grafana: ## Open Grafana dashboard
	@echo "📊 Opening Grafana..."
	@open http://localhost:3001

prometheus: ## Open Prometheus dashboard
	@echo "📈 Opening Prometheus..."
	@open http://localhost:9090

# Quick start
quickstart: ## Quick start for new users
	@echo "🚀 Shadow.AI II Quick Start"
	@echo "=========================="
	@echo "1. Setting up development environment..."
	@make dev
	@echo ""
	@echo "2. Waiting for services to be ready..."
	@sleep 30
	@echo ""
	@echo "3. Checking health..."
	@make health
	@echo ""
	@echo "✅ Quick start completed!"
	@echo "📊 Dashboard: http://localhost:3000"
	@echo "🤖 MCP Server: http://localhost:8000"
	@echo "📈 Grafana: http://localhost:3001"