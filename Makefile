# AI Teacher - Docker Management Makefile
# Provides convenient commands for Docker operations

.PHONY: help build up down restart logs clean backup

# Default target
help:
	@echo "AI Teacher - Docker Commands"
	@echo "============================"
	@echo ""
	@echo "Setup:"
	@echo "  make setup       - Initial setup (copy .env, build, start)"
	@echo "  make build       - Build Docker images"
	@echo ""
	@echo "Running:"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo ""
	@echo "Monitoring:"
	@echo "  make logs        - View logs (all services)"
	@echo "  make logs-backend  - View backend logs only"
	@echo "  make logs-frontend - View frontend logs only"
	@echo "  make ps          - Show running containers"
	@echo "  make stats       - Show container resource usage"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       - Remove containers and images"
	@echo "  make clean-all   - Remove containers, images, and volumes"
	@echo "  make backup      - Backup data volumes"
	@echo "  make shell-backend  - Open shell in backend container"
	@echo "  make shell-frontend - Open shell in frontend container"
	@echo ""
	@echo "Development:"
	@echo "  make rebuild     - Rebuild and restart (no cache)"
	@echo "  make test        - Run backend tests"

# Initial setup
setup:
	@echo "Setting up AI Teacher..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from .env.example..."; \
		cp .env.example .env; \
		echo "Please edit .env file with your API keys"; \
		exit 1; \
	fi
	@echo "Building Docker images..."
	docker compose build
	@echo "Starting services..."
	docker compose up -d
	@echo ""
	@echo "Setup complete!"
	@echo "Frontend: http://localhost:4200"
	@echo "Backend: http://localhost:8000/docs"

# Build images
build:
	docker compose build

# Rebuild without cache
rebuild:
	docker compose build --no-cache
	docker compose up -d

# Start services
up:
	docker compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:4200"
	@echo "Backend: http://localhost:8000/docs"

# Stop services
down:
	docker compose down

# Restart services
restart:
	docker compose restart

# View logs
logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

# Show container status
ps:
	docker compose ps

# Show resource usage
stats:
	docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Clean up
clean:
	docker compose down
	docker compose rm -f
	docker image prune -f

clean-all:
	@echo "WARNING: This will remove all data volumes!"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read dummy
	docker compose down -v
	docker image prune -a -f
	docker volume prune -f

# Backup volumes
backup:
	@mkdir -p backups
	@echo "Backing up ChromaDB..."
	@docker run --rm \
		-v ai_teacher_chroma_data:/data \
		-v $$(pwd)/backups:/backup \
		alpine tar czf /backup/chroma_$$(date +%Y%m%d_%H%M%S).tar.gz /data
	@echo "Backing up uploads..."
	@docker run --rm \
		-v ai_teacher_uploads_data:/data \
		-v $$(pwd)/backups:/backup \
		alpine tar czf /backup/uploads_$$(date +%Y%m%d_%H%M%S).tar.gz /data
	@echo "Backup complete! Files in ./backups/"

# Shell access
shell-backend:
	docker compose exec backend bash

shell-frontend:
	docker compose exec frontend sh

# Run tests
test:
	docker compose exec backend pytest -v

# Health check
health:
	@echo "Checking backend health..."
	@curl -f http://localhost:8000/health || echo "Backend unhealthy"
	@echo ""
	@echo "Checking frontend health..."
	@curl -f http://localhost:4200/health || echo "Frontend unhealthy"
