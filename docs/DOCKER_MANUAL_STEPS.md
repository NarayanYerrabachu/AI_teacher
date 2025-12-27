# AI Teacher - Manual Docker Setup Steps

Follow these steps to run AI Teacher in Docker manually.

## Prerequisites Check

```bash
# Verify Docker is running
docker ps

# Verify you're in the project directory
cd /home/evocenta/PycharmProjects/AI_teacher
pwd
```

## Step 1: Fix Permissions (If Needed)

If you encounter permission errors with Docker:

```bash
# Check Docker group membership
groups | grep docker

# If not in docker group, add yourself (requires logout/login after)
sudo usermod -aG docker $USER

# Or fix the buildx lock file
sudo chown -R $USER:$USER ~/.docker
```

## Step 2: Prepare Environment

```bash
# Verify .env file exists
ls -la .env

# Check API keys are set
cat .env | grep -E "OPENAI_API_KEY|EXA_API_KEY"

# If .env doesn't exist, create it
cp .env.example .env
nano .env  # Edit with your API keys
```

## Step 3: Ensure Pipfile is in Backend Directory

```bash
# Copy Pipfile to backend directory (already done, but verify)
cp Pipfile Pipfile.lock backend/
ls backend/ | grep Pipfile
```

## Step 4: Build Docker Images

**Option A: Using Make (Recommended)**
```bash
make build
```

**Option B: Using Docker Compose V2**
```bash
# Remove obsolete version warning (optional)
sed -i '/^version:/d' docker-compose.yml

# Build without BuildKit (if you have permission issues)
DOCKER_BUILDKIT=0 docker compose build

# Or with BuildKit (faster, but requires permissions)
docker compose build
```

**Note:** First build takes 10-15 minutes because it:
- Downloads Python 3.12 base image
- Installs system dependencies
- Installs all Python packages (LangChain, ChromaDB, FastAPI, etc.)
- Downloads Node 20 base image
- Installs npm packages
- Builds React frontend

## Step 5: Start Services

**Option A: Using Make**
```bash
# Start in detached mode
make up

# Or start with logs visible
docker compose up
```

**Option B: Using Docker Compose**
```bash
# Start in detached mode (background)
docker compose up -d

# Or start with logs visible
docker compose up
```

## Step 6: Monitor Startup

```bash
# Watch logs from all services
docker compose logs -f

# Watch backend logs only
docker compose logs -f backend

# Watch frontend logs only
docker compose logs -f frontend

# Check container status
docker compose ps

# Check health status
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

## Step 7: Verify Services are Running

```bash
# Check if containers are running
docker ps

# Test backend health
curl http://localhost:8000/health

# Test frontend (should return HTML)
curl http://localhost:4200

# Open in browser
# Frontend: http://localhost:4200
# Backend API Docs: http://localhost:8000/docs
```

## Step 8: Test the Application

1. **Open browser** to http://localhost:4200
2. **Test chat**: Type a question
3. **Upload PDF**: Use the API docs at http://localhost:8000/docs
4. **Check logs**: `docker compose logs -f backend`

## Common Issues & Solutions

### Issue: Port Already in Use

```bash
# Find what's using the port
sudo lsof -i :8000
sudo lsof -i :4200

# Kill the process
sudo kill -9 <PID>

# Or change ports in docker-compose.yml
nano docker-compose.yml
# Change "8000:8000" to "9000:8000"
# Change "4200:4200" to "3000:4200"
```

### Issue: Build Fails with Permission Error

```bash
# Fix Docker permissions
sudo chown -R $USER:$USER ~/.docker

# Or build without BuildKit
DOCKER_BUILDKIT=0 docker compose build
```

### Issue: Build is Too Slow

```bash
# Use requirements.txt instead of Pipfile (faster)
# Create requirements.txt
pipenv requirements > backend/requirements.txt

# Edit backend/Dockerfile, replace lines 16-19:
# FROM:
#   COPY Pipfile Pipfile.lock ./
#   RUN pipenv install --system --deploy --ignore-pipfile
# TO:
#   COPY requirements.txt ./
#   RUN pip install --no-cache-dir -r requirements.txt

# Rebuild
docker compose build --no-cache backend
```

### Issue: Container Keeps Restarting

```bash
# Check logs for errors
docker compose logs backend

# Common issues:
# - Missing API keys in .env
# - Port conflicts
# - Insufficient memory

# Restart containers
docker compose restart
```

### Issue: Cannot Connect to Backend from Frontend

```bash
# Verify both containers are on same network
docker network inspect ai_teacher_ai-teacher-network

# Check nginx proxy configuration
docker compose exec frontend cat /etc/nginx/conf.d/default.conf

# Test backend from frontend container
docker compose exec frontend wget -O- http://backend:8000/health
```

## Management Commands

### Stop Services
```bash
# Stop containers (keep data)
docker compose stop

# Stop and remove containers (keep data)
docker compose down

# Stop and remove everything including volumes (DELETES DATA!)
docker compose down -v
```

### Restart Services
```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart frontend
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend
```

### Access Container Shell
```bash
# Backend shell
docker compose exec backend bash

# Frontend shell
docker compose exec frontend sh

# As root (for debugging)
docker compose exec -u root backend bash
```

### Clean Up
```bash
# Remove stopped containers
docker compose rm

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything (nuclear option)
docker system prune -a --volumes
```

## Backup Data

```bash
# Create backup directory
mkdir -p backups

# Backup ChromaDB
docker run --rm \
  -v ai_teacher_chroma_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/chroma_$(date +%Y%m%d_%H%M%S).tar.gz /data

# Backup uploads
docker run --rm \
  -v ai_teacher_uploads_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/uploads_$(date +%Y%m%d_%H%M%S).tar.gz /data

echo "Backups saved to ./backups/"
```

## Update Application

```bash
# Pull latest code
git pull

# Rebuild images
docker compose build

# Restart services
docker compose up -d

# Verify
docker compose ps
docker compose logs -f
```

## Complete Teardown and Fresh Start

```bash
# Stop everything
docker compose down -v

# Remove images
docker rmi ai_teacher-backend ai_teacher-frontend

# Remove all unused Docker resources
docker system prune -a --volumes

# Rebuild from scratch
docker compose build --no-cache

# Start fresh
docker compose up -d
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker compose build` | Build images |
| `docker compose up -d` | Start services (detached) |
| `docker compose up` | Start services (with logs) |
| `docker compose down` | Stop and remove containers |
| `docker compose ps` | Show running containers |
| `docker compose logs -f` | Follow logs |
| `docker compose restart` | Restart services |
| `docker compose exec backend bash` | Backend shell |
| `docker ps` | List running containers |
| `docker images` | List images |

## Troubleshooting Checklist

- [ ] Docker service is running: `systemctl status docker`
- [ ] .env file exists with API keys
- [ ] Ports 8000 and 4200 are free
- [ ] Sufficient disk space: `df -h`
- [ ] Sufficient memory: `free -h`
- [ ] Docker permissions correct: `groups | grep docker`
- [ ] Pipfile is in backend directory
- [ ] Images built successfully: `docker images`
- [ ] Containers running: `docker compose ps`
- [ ] Health checks passing: `curl http://localhost:8000/health`

## Need Help?

Check the full documentation:
- **Quick Start**: `DOCKER_QUICKSTART.md`
- **Complete Guide**: `DOCKER_DEPLOYMENT.md`
- **Architecture**: `SYSTEM_ARCHITECTURE.md`

---

**Good luck!** 🚀

Once running, access:
- Frontend: http://localhost:4200
- Backend API: http://localhost:8000/docs
