.PHONY: help build up down restart logs ps clean test report shell

# Default target
help:
	@echo "Deep Instinct to Mattermost - Docker Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs (all services)"
	@echo "  make logs-monitor   - View monitor logs"
	@echo "  make logs-report    - View report server logs"
	@echo "  make logs-daily     - View daily report logs"
	@echo "  make ps             - Show service status"
	@echo "  make report         - Run daily report manually"
	@echo "  make report-date    - Run report for specific date (DATE=2026-02-13)"
	@echo "  make shell          - Open shell in monitor container"
	@echo "  make shell-report   - Open shell in report server"
	@echo "  make test           - Test API connection"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make clean-all      - Remove everything including images"
	@echo "  make backup         - Backup event_detail directory"
	@echo "  make health         - Check service health"
	@echo "  make stats          - Show resource usage"
	@echo ""

# Build images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

# Start services
up:
	@echo "🚀 Starting services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@make ps

# Stop services
down:
	@echo "🛑 Stopping services..."
	docker-compose down
	@echo "✅ Services stopped!"

# Restart services
restart:
	@echo "🔄 Restarting services..."
	docker-compose restart
	@echo "✅ Services restarted!"

# View logs
logs:
	docker-compose logs -f

logs-monitor:
	docker-compose logs -f monitor

logs-report:
	docker-compose logs -f report-server

logs-daily:
	docker-compose logs -f daily-report

# Show status
ps:
	@echo "📊 Service Status:"
	@docker-compose ps

# Run daily report manually
report:
	@echo "📊 Running daily report..."
	docker-compose run --rm daily-report once
	@echo "✅ Report generated!"

# Run report for specific date
report-date:
ifndef DATE
	@echo "❌ Please specify DATE variable: make report-date DATE=2026-02-13"
	@exit 1
endif
	@echo "📊 Running report for $(DATE)..."
	docker-compose run --rm daily-report once $(DATE)
	@echo "✅ Report generated!"

# Open shell
shell:
	@echo "🐚 Opening shell in monitor container..."
	docker-compose run --rm monitor /bin/bash

shell-report:
	@echo "🐚 Opening shell in report-server container..."
	docker-compose run --rm report-server /bin/bash

# Test connection
test:
	@echo "🧪 Testing API connection..."
	docker-compose run --rm monitor python3 test_connection.py

# Clean up
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose down -v
	@echo "✅ Cleaned!"

clean-all: clean
	@echo "🧹 Removing images..."
	docker-compose down -v --rmi all
	@echo "✅ All cleaned!"

# Backup
backup:
	@echo "💾 Creating backup..."
	@mkdir -p backups
	@tar -czf backups/backup-$$(date +%Y%m%d-%H%M%S).tar.gz event_detail/ logs/
	@echo "✅ Backup created in backups/"
	@ls -lh backups/ | tail -1

# Health check
health:
	@echo "🏥 Checking service health..."
	@docker inspect --format='{{.Name}}: {{.State.Health.Status}}' $$(docker-compose ps -q) 2>/dev/null || echo "Health checks not available"

# Resource stats
stats:
	@echo "📈 Resource Usage:"
	@docker stats --no-stream $$(docker-compose ps -q)

# Development commands
dev-build:
	@echo "🔨 Building for development..."
	docker-compose -f docker-compose.yml -f docker-compose.override.yml build

dev-up:
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

dev-logs:
	docker-compose -f docker-compose.yml -f docker-compose.override.yml logs -f

# Install (first time setup)
install:
	@echo "📦 First time setup..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from template..."; \
		cp .env.docker .env; \
		echo "⚠️  Please edit .env file with your credentials!"; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@mkdir -p event_detail logs
	@echo "Building images..."
	@make build
	@echo ""
	@echo "✅ Installation complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env file with your credentials"
	@echo "  2. Run: make up"
	@echo "  3. Check logs: make logs"
