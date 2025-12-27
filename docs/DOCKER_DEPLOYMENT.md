# AI Teacher - Docker Deployment Guide

Complete guide for containerizing and deploying AI Teacher with Docker.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Building & Running](#building--running)
- [Accessing Services](#accessing-services)
- [Data Persistence](#data-persistence)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## Prerequisites

### Required Software
- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0+ (included with Docker Desktop)

### Verify Installation
```bash
docker --version
docker-compose --version
```

## Quick Start

### 1. Clone and Navigate
```bash
cd /home/evocenta/PycharmProjects/AI_teacher
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env  # or vim, code, etc.
```

**Required API Keys:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `EXA_API_KEY`: Your Exa.ai API key for web search

### 3. Build and Run
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Or for specific service
docker-compose logs -f backend
```

### 4. Access Application
- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 5. Stop Services
```bash
# Stop containers
docker-compose down

# Stop and remove volumes (deletes data!)
docker-compose down -v
```

## Architecture

### Docker Services

```
┌─────────────────────────────────────────────────┐
│                   Host System                   │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │        Docker Network (bridge)            │ │
│  │                                           │ │
│  │  ┌────────────────┐  ┌─────────────────┐ │ │
│  │  │   Frontend     │  │    Backend      │ │ │
│  │  │   (nginx)      │  │   (FastAPI)     │ │ │
│  │  │   Port: 4200   │  │   Port: 8000    │ │ │
│  │  │                │  │                 │ │ │
│  │  │  /usr/share/   │  │  /app/          │ │ │
│  │  │  nginx/html    │  │                 │ │ │
│  │  └────────────────┘  └─────────────────┘ │ │
│  │          │                    │          │ │
│  │          │                    │          │ │
│  │          └──── API Proxy ─────┘          │ │
│  │                                           │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │          Docker Volumes                   │ │
│  │                                           │ │
│  │  • chroma_data  → /app/chroma_db         │ │
│  │  • uploads_data → /app/uploads           │ │
│  │  • ./logs       → /app/logs              │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Container Details

#### Backend Container
- **Base Image**: python:3.12-slim
- **Build**: Multi-stage (builder + production)
- **User**: Non-root (appuser, uid 1000)
- **Health Check**: `/health` endpoint every 30s
- **Volumes**:
  - `chroma_data`: ChromaDB vector database
  - `uploads_data`: Uploaded PDF files
  - `./logs`: Application logs

#### Frontend Container
- **Base Image**: nginx:alpine
- **Build**: Multi-stage (Node build + nginx serve)
- **User**: Non-root (appuser, uid 1000)
- **Features**:
  - Gzip compression
  - API proxy to backend
  - SPA routing support
  - Static asset caching

## Configuration

### Environment Variables

All configuration is managed through `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...
OPENAI_API_BASE=https://api.openai.com/v1
USE_OPENAI_EMBEDDINGS=true
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=384

# LLM Configuration
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
MAX_HISTORY_MESSAGES=10

# Vector Database
CHROMA_PERSIST_DIR=./chroma_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
DEFAULT_SEARCH_K=4

# Web Search
EXA_API_KEY=your-exa-api-key
WEB_SEARCH_RESULTS_LIMIT=3
WEB_SEARCH_DAYS_BACK=90

# Agent Configuration
USE_HYBRID_AGENT=true

# Logging
LOG_LEVEL=INFO
```

### Port Configuration

Default ports can be changed in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8000:8000"  # Change left side: "9000:8000"

  frontend:
    ports:
      - "4200:4200"  # Change left side: "3000:4200"
```

## Building & Running

### Development Mode

```bash
# Build images
docker-compose build

# Start services with logs
docker-compose up

# Start in detached mode
docker-compose up -d

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend
```

### Production Mode

```bash
# Build with no cache (clean build)
docker-compose build --no-cache

# Start with restart policy
docker-compose up -d

# Scale services (if needed)
docker-compose up -d --scale backend=2
```

### Useful Commands

```bash
# View running containers
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash
docker-compose exec frontend sh

# Restart specific service
docker-compose restart backend

# Stop all services
docker-compose stop

# Remove all containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

## Accessing Services

### Frontend (React App)
```
URL: http://localhost:4200
```

### Backend API
```
URL: http://localhost:8000
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
Health: http://localhost:8000/health
```

### Container Shell Access

```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh

# As root (for debugging)
docker-compose exec -u root backend bash
```

## Data Persistence

### Docker Volumes

Data is persisted using Docker volumes:

1. **chroma_data**: Vector database storage
2. **uploads_data**: Uploaded PDF files
3. **./logs**: Application logs (bind mount)

### Managing Volumes

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect ai_teacher_chroma_data

# Backup volume
docker run --rm -v ai_teacher_chroma_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/chroma_backup.tar.gz /data

# Restore volume
docker run --rm -v ai_teacher_chroma_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/chroma_backup.tar.gz -C /

# Remove unused volumes
docker volume prune
```

### Data Location

Volume data is stored in:
- **Linux**: `/var/lib/docker/volumes/`
- **macOS**: `~/Library/Containers/com.docker.docker/Data/`
- **Windows**: `\\wsl$\docker-desktop-data\data\docker\volumes\`

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Check container status
docker-compose ps

# Inspect container
docker inspect ai-teacher-backend
```

### API Key Not Found

```bash
# Verify .env file exists
cat .env | grep OPENAI_API_KEY

# Restart containers to reload environment
docker-compose down
docker-compose up -d

# Check environment inside container
docker-compose exec backend env | grep OPENAI
```

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000
# or
sudo netstat -nlp | grep :8000

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

### Permission Denied

```bash
# Fix volume permissions
docker-compose exec -u root backend chown -R appuser:appuser /app/chroma_db
docker-compose exec -u root backend chown -R appuser:appuser /app/uploads

# Or rebuild with correct permissions
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### ChromaDB Issues

```bash
# Clear ChromaDB volume
docker-compose down
docker volume rm ai_teacher_chroma_data
docker-compose up -d

# Or backup and restore
docker-compose exec backend rm -rf /app/chroma_db/*
docker-compose restart backend
```

### Out of Disk Space

```bash
# Remove unused images
docker image prune -a

# Remove unused containers
docker container prune

# Remove unused volumes
docker volume prune

# Remove everything
docker system prune -a --volumes
```

## Production Deployment

### Security Hardening

1. **Use Secrets Management**
```yaml
# docker-compose.prod.yml
services:
  backend:
    secrets:
      - openai_api_key
      - exa_api_key

secrets:
  openai_api_key:
    file: ./secrets/openai.txt
  exa_api_key:
    file: ./secrets/exa.txt
```

2. **Enable HTTPS (with Nginx Reverse Proxy)**
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
```

3. **Resource Limits**
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Logging Configuration

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Health Checks

Built-in health checks monitor service health:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Monitoring

```bash
# Container stats
docker stats

# Specific container
docker stats ai-teacher-backend

# All containers
docker-compose top
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh - Automated backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$DATE"

mkdir -p $BACKUP_DIR

# Backup volumes
docker run --rm \
  -v ai_teacher_chroma_data:/data \
  -v $(pwd)/$BACKUP_DIR:/backup \
  alpine tar czf /backup/chroma.tar.gz /data

docker run --rm \
  -v ai_teacher_uploads_data:/data \
  -v $(pwd)/$BACKUP_DIR:/backup \
  alpine tar czf /backup/uploads.tar.gz /data

# Backup config
cp .env $BACKUP_DIR/
cp docker-compose.yml $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

### CI/CD Integration

```yaml
# .github/workflows/docker.yml
name: Docker Build and Push

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build images
        run: docker-compose build

      - name: Run tests
        run: docker-compose run backend pytest

      - name: Push to registry
        run: |
          docker tag ai-teacher-backend:latest registry.example.com/ai-teacher-backend:latest
          docker push registry.example.com/ai-teacher-backend:latest
```

## Performance Optimization

### Multi-Stage Builds
Already implemented in Dockerfiles for smaller image sizes.

### Layer Caching
Order Dockerfile instructions from least to most frequently changed:
1. System dependencies
2. Application dependencies
3. Application code

### BuildKit
Enable Docker BuildKit for faster builds:
```bash
export DOCKER_BUILDKIT=1
docker-compose build
```

## Appendix

### File Structure
```
AI_teacher/
├── docker-compose.yml        # Main orchestration file
├── .env                       # Environment variables
├── backend/
│   ├── Dockerfile            # Backend container definition
│   ├── .dockerignore         # Exclude files from build
│   └── ...
├── frontend/
│   ├── Dockerfile            # Frontend container definition
│   ├── .dockerignore         # Exclude files from build
│   ├── nginx.conf            # Nginx configuration
│   └── ...
└── logs/                     # Application logs (bind mount)
```

### Useful Resources
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)

---

**Last Updated**: 2025-12-26
**Version**: 1.0
