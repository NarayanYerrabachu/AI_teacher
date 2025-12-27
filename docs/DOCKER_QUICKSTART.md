# AI Teacher - Docker Quick Start

Get AI Teacher running in Docker in under 5 minutes!

## Prerequisites

- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop/))
- OpenAI API key ([Get key](https://platform.openai.com/api-keys))
- Exa.ai API key ([Get key](https://exa.ai/))

## Quick Start (3 Steps)

### 1. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env  # or code .env, vim .env, etc.
```

**Required keys to update:**
```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
EXA_API_KEY=your-exa-key-here
```

### 2. Build & Start

```bash
# Using Make (recommended)
make setup

# OR using docker-compose directly
docker-compose up -d
```

### 3. Access Application

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000/docs

That's it! 🎉

## Using Makefile Commands

The Makefile provides convenient shortcuts:

```bash
# Start services
make up

# View logs
make logs

# Stop services
make down

# Restart
make restart

# See all commands
make help
```

## Common Operations

### View Logs
```bash
# All services
make logs

# Backend only
make logs-backend

# Frontend only
make logs-frontend
```

### Check Status
```bash
# List running containers
make ps

# Resource usage
make stats

# Health check
make health
```

### Maintenance
```bash
# Backup data
make backup

# Clean up
make clean

# Clean everything (including data!)
make clean-all
```

### Development
```bash
# Rebuild from scratch
make rebuild

# Access backend shell
make shell-backend

# Access frontend shell
make shell-frontend
```

## Troubleshooting

### Port Already in Use

```bash
# Change ports in docker-compose.yml
services:
  backend:
    ports:
      - "9000:8000"  # Change 8000 to 9000

  frontend:
    ports:
      - "3000:4200"  # Change 4200 to 3000
```

### API Key Errors

```bash
# Verify .env file
cat .env | grep API_KEY

# Restart to reload environment
make restart
```

### Container Won't Start

```bash
# Check logs
make logs

# Rebuild
make rebuild
```

### Reset Everything

```bash
# Stop and remove all containers, images, volumes
make clean-all

# Start fresh
make setup
```

## Architecture

```
┌─────────────────────────────────────┐
│         Host (Your Computer)        │
│                                     │
│  Port 4200 → Frontend (nginx)      │
│  Port 8000 → Backend (FastAPI)     │
│                                     │
│  Volumes:                           │
│  - chroma_data  (Vector DB)        │
│  - uploads_data (PDF files)        │
│  - ./logs       (Application logs) │
└─────────────────────────────────────┘
```

## Data Persistence

Your data is stored in Docker volumes and persists across container restarts:

- **ChromaDB**: Vector database with embedded documents
- **Uploads**: PDF files you've uploaded
- **Logs**: Application logs in `./logs/` directory

## Backup Your Data

```bash
# Automated backup
make backup

# Backup files saved to ./backups/
```

## Next Steps

- Read [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for detailed documentation
- Check [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) for system design
- Upload PDFs via API: `curl -X POST "http://localhost:8000/upload-pdf" -F "files=@document.pdf"`

## Support

For issues, check:
1. Docker logs: `make logs`
2. Container status: `make ps`
3. Health: `make health`
4. Full guide: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

---

**Quick Commands Reference:**

| Command | Description |
|---------|-------------|
| `make setup` | Initial setup |
| `make up` | Start services |
| `make down` | Stop services |
| `make logs` | View logs |
| `make restart` | Restart services |
| `make backup` | Backup data |
| `make clean` | Remove containers |
| `make help` | Show all commands |
