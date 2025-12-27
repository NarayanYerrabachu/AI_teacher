# AI Teacher - Docker on Windows Guide

## ✅ Good News: Everything Works on Windows!

Your Docker setup is **cross-platform compatible** and will run on Windows with Docker Desktop installed.

## Prerequisites for Windows

### 1. Install Docker Desktop
- **Download**: https://www.docker.com/products/docker-desktop/
- **Requirements**: Windows 10/11 (64-bit), WSL 2 enabled
- **Install**: Run installer, restart computer
- **Verify**: Open PowerShell and run:
  ```powershell
  docker --version
  docker compose version
  ```

### 2. Enable WSL 2 (if not enabled)
Docker Desktop for Windows uses WSL 2 (Windows Subsystem for Linux):

```powershell
# Run PowerShell as Administrator
wsl --install
wsl --set-default-version 2
```

Restart your computer after installation.

## Running on Windows

### Method 1: Using PowerShell/CMD (Recommended)

All Docker Compose commands work identically on Windows:

```powershell
# Navigate to project
cd C:\path\to\AI_teacher

# Verify .env file exists
dir .env

# Build images (first time only, takes 10-15 minutes)
docker compose build

# Start services
docker compose up -d

# View logs
docker compose logs -f

# Check status
docker compose ps

# Stop services
docker compose down
```

### Method 2: Using Windows Command Prompt

Same commands work in CMD:

```cmd
cd C:\path\to\AI_teacher
docker compose up -d
docker compose logs -f
docker compose ps
```

### Method 3: Using Git Bash (if installed)

If you have Git for Windows, you can use the Makefile:

```bash
# In Git Bash
cd /c/path/to/AI_teacher
make setup
make up
make logs
```

## What Works Without Changes

✅ **docker-compose.yml** - Works identically
✅ **Dockerfiles** - Work identically
✅ **Port bindings** - 8000:8000, 4200:4200 work the same
✅ **Named volumes** - chroma_data, uploads_data work the same
✅ **Environment variables** - .env file works the same
✅ **Health checks** - Work identically
✅ **Networking** - Container networking works the same

## Potential Issues & Solutions

### Issue 1: Line Endings (CRLF vs LF)

**Problem**: Windows uses CRLF (`\r\n`), Linux uses LF (`\n`). This can cause issues in Dockerfiles and scripts.

**Solution**: Configure Git to handle line endings:

```powershell
# Configure Git to checkout as-is, commit as LF
git config --global core.autocrlf input

# Or for this repo only (in project directory)
git config core.autocrlf input

# Re-clone or reset files
git rm -rf --cached .
git reset --hard
```

### Issue 2: Makefile Won't Work in CMD/PowerShell

**Problem**: `make` commands require Unix tools.

**Solutions**:

**Option A: Install Make for Windows**
```powershell
# Using Chocolatey (package manager)
choco install make

# Using Scoop (package manager)
scoop install make
```

**Option B: Use Git Bash** (comes with Git for Windows)
```bash
# All make commands work in Git Bash
make up
make logs
make down
```

**Option C: Use Docker Compose Directly** (No make needed)

Instead of Makefile commands, use these equivalents:

| Makefile Command | Windows PowerShell/CMD Equivalent |
|------------------|-----------------------------------|
| `make setup` | `docker compose build && docker compose up -d` |
| `make up` | `docker compose up -d` |
| `make down` | `docker compose down` |
| `make logs` | `docker compose logs -f` |
| `make logs-backend` | `docker compose logs -f backend` |
| `make restart` | `docker compose restart` |
| `make ps` | `docker compose ps` |
| `make clean` | `docker compose down && docker image prune -f` |
| `make backup` | See backup script below |
| `make shell-backend` | `docker compose exec backend bash` |

### Issue 3: Shell Scripts Won't Run

**Problem**: `.sh` scripts are for bash, not CMD/PowerShell.

**Solutions**:

**Option A: Use Git Bash or WSL**
```bash
./start-all.sh
```

**Option B: Create PowerShell Equivalents**

Create `start-all.ps1`:
```powershell
# Start AI Teacher in Docker
Write-Host "Starting AI Teacher..." -ForegroundColor Green
docker compose up -d
Write-Host "Frontend: http://localhost:4200" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000/docs" -ForegroundColor Cyan
```

Run with:
```powershell
.\start-all.ps1
```

**Option C: Use Docker Compose Directly**
```powershell
docker compose up -d
```

## Complete Windows Workflow

### First Time Setup

1. **Clone/Copy Project**
   ```powershell
   cd C:\Users\YourName\Projects
   # Copy project or clone from git
   ```

2. **Create .env File**
   ```powershell
   cd AI_teacher
   copy .env.example .env
   notepad .env  # Edit with your API keys
   ```

3. **Build Images**
   ```powershell
   docker compose build
   # Takes 10-15 minutes first time
   ```

4. **Start Services**
   ```powershell
   docker compose up -d
   ```

5. **Access Application**
   - Open browser: http://localhost:4200
   - API docs: http://localhost:8000/docs

### Daily Usage

```powershell
# Start
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down

# Restart
docker compose restart
```

## Windows-Specific Tips

### 1. Use Docker Desktop Dashboard

Docker Desktop provides a GUI to:
- View running containers
- See logs
- Restart containers
- Access container shell
- Manage volumes

Access: System tray → Docker icon → Dashboard

### 2. Volume Performance

On Windows, Docker volumes are stored in WSL 2. For best performance:

```powershell
# Volumes are in WSL 2 filesystem
# Access via: \\wsl$\docker-desktop-data\data\docker\volumes
```

### 3. Port Conflicts on Windows

Check if ports are in use:

```powershell
# Check port 8000
netstat -ano | findstr :8000

# Check port 4200
netstat -ano | findstr :4200

# Kill process by PID
taskkill /PID <PID> /F
```

### 4. Firewall Issues

If containers can't communicate:

1. Open Windows Defender Firewall
2. Allow Docker Desktop through firewall
3. Or disable firewall for private networks (dev only)

### 5. Resource Allocation

Docker Desktop Settings → Resources:

- **CPUs**: Allocate at least 2 CPUs
- **Memory**: Allocate at least 4 GB RAM
- **Disk**: Ensure sufficient space (10+ GB)

## Backup on Windows

PowerShell script for backup:

```powershell
# backup.ps1
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backups\$date"
New-Item -ItemType Directory -Force -Path $backupDir

Write-Host "Backing up ChromaDB..." -ForegroundColor Yellow
docker run --rm `
  -v ai_teacher_chroma_data:/data `
  -v ${PWD}\$backupDir:/backup `
  alpine tar czf /backup/chroma.tar.gz /data

Write-Host "Backing up uploads..." -ForegroundColor Yellow
docker run --rm `
  -v ai_teacher_uploads_data:/data `
  -v ${PWD}\$backupDir:/backup `
  alpine tar czf /backup/uploads.tar.gz /data

Write-Host "Backup complete: $backupDir" -ForegroundColor Green
```

Run with:
```powershell
.\backup.ps1
```

## Troubleshooting Windows-Specific Issues

### Docker Desktop Not Starting

1. **Enable Virtualization** in BIOS
2. **Enable Hyper-V**:
   ```powershell
   # PowerShell as Administrator
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   ```
3. **Update Windows** to latest version
4. **Reinstall Docker Desktop**

### "access denied" or "permission denied"

Run PowerShell as Administrator:
```powershell
# Right-click PowerShell → Run as Administrator
docker compose up -d
```

### WSL 2 Issues

```powershell
# Update WSL
wsl --update

# Restart WSL
wsl --shutdown

# Restart Docker Desktop
```

### Line Ending Errors

```powershell
# Fix line endings
git config core.autocrlf input
git rm -rf --cached .
git reset --hard
```

### Build Fails with "no space left"

Clear Docker cache:
```powershell
docker system prune -a --volumes
# Warning: This removes all unused containers, images, volumes
```

## Quick Reference - Windows Commands

### Start/Stop
```powershell
docker compose up -d          # Start detached
docker compose up             # Start with logs
docker compose down           # Stop and remove
docker compose stop           # Stop without removing
docker compose restart        # Restart all services
```

### Monitoring
```powershell
docker compose ps             # List containers
docker compose logs -f        # Follow all logs
docker compose logs backend   # Backend logs only
docker compose top            # Show running processes
docker stats                  # Resource usage
```

### Management
```powershell
docker compose build          # Build images
docker compose pull           # Pull images
docker compose exec backend bash     # Backend shell
docker compose exec frontend sh      # Frontend shell
```

### Cleanup
```powershell
docker compose down -v        # Remove with volumes (deletes data!)
docker system prune           # Remove unused containers/images
docker volume prune           # Remove unused volumes
```

## Performance Tips for Windows

1. **Store project in WSL 2 filesystem** (faster):
   ```powershell
   wsl
   cd ~
   git clone <repo>
   code .
   ```

2. **Allocate more resources** in Docker Desktop settings

3. **Use BuildKit** for faster builds:
   ```powershell
   $env:DOCKER_BUILDKIT=1
   docker compose build
   ```

4. **Enable file sharing** for volumes in Docker Desktop settings

## Accessing from Other Devices

If you want to access from other devices on your network:

1. **Find your IP**:
   ```powershell
   ipconfig
   # Look for IPv4 Address
   ```

2. **Access from other devices**:
   - Frontend: `http://YOUR_IP:4200`
   - Backend: `http://YOUR_IP:8000/docs`

3. **Configure Windows Firewall** to allow ports 8000 and 4200

## Summary

### ✅ What Just Works
- Docker Compose commands (identical to Linux)
- Container networking
- Port bindings
- Environment variables
- Volumes (via WSL 2)
- Health checks

### ⚠️ What May Need Adjustment
- Line endings (configure Git)
- Makefile (use Git Bash or translate to PowerShell)
- Shell scripts (use PowerShell equivalents)

### 🎯 Recommended Windows Setup
1. Install Docker Desktop
2. Install Git for Windows (includes Git Bash)
3. Use PowerShell for docker compose commands
4. Use Git Bash for make commands (if preferred)
5. Configure Git for line endings

---

**Bottom Line**: Your Docker setup is **fully compatible** with Windows. Just install Docker Desktop and use the same `docker compose` commands!

**Quick Start on Windows**:
```powershell
cd C:\path\to\AI_teacher
docker compose build
docker compose up -d
# Open http://localhost:4200
```

That's it! 🚀
