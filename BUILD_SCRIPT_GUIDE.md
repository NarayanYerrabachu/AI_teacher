# Build Script Guide for Ubuntu Linux

## Quick Start

### 1. Make Script Executable
```bash
chmod +x build.sh
```

### 2. Run Setup (First Time)
```bash
./build.sh setup
```

This will:
- Check/create .env file
- Build all Docker images (15-20 minutes)
- Start services
- Display access URLs

## All Available Commands

### Setup & Installation
```bash
./build.sh install-docker    # Install Docker on Ubuntu (first time only)
./build.sh setup             # Complete setup (first time)
```

### Build Commands
```bash
./build.sh build             # Build all images
./build.sh build-backend     # Build backend only
./build.sh build-frontend    # Build frontend only
./build.sh rebuild           # Rebuild without cache
```

### Service Management
```bash
./build.sh start             # Start all services
./build.sh stop              # Stop all services
./build.sh restart           # Restart services
./build.sh status            # Show container status
```

### Monitoring
```bash
./build.sh logs              # View all logs
./build.sh logs-backend      # Backend logs only
./build.sh logs-frontend     # Frontend logs only
./build.sh stats             # Resource usage
./build.sh health            # Health check
```

### Maintenance
```bash
./build.sh clean             # Remove containers/images
./build.sh clean-all         # Remove everything (including data!)
./build.sh prune             # Clean Docker system
./build.sh backup            # Backup data volumes
```

### Shell Access
```bash
./build.sh shell-backend     # Access backend container
./build.sh shell-frontend    # Access frontend container
```

## Common Workflows

### First Time Setup
```bash
# 1. Make script executable
chmod +x build.sh

# 2. Run setup
./build.sh setup

# 3. Check status
./build.sh status

# 4. View logs
./build.sh logs-backend
```

### Daily Development
```bash
# Make code changes...

# Rebuild and restart
./build.sh build
./build.sh restart

# Check logs
./build.sh logs
```

### Quick Build & Start
```bash
./build.sh build && ./build.sh start
```

### Monitor Services
```bash
# Check health
./build.sh health

# View logs
./build.sh logs-backend

# Check resource usage
./build.sh stats
```

### Clean Up
```bash
# Stop services
./build.sh stop

# Clean up containers
./build.sh clean

# Full cleanup (removes data!)
./build.sh clean-all
```

## Script Features

### ✅ Automatic Checks
- Verifies Docker is installed
- Checks Docker daemon is running
- Validates permissions

### ✅ Colored Output
- Green: Success messages
- Red: Error messages
- Yellow: Warnings
- Blue: Info messages

### ✅ Safety Features
- Confirmation prompts for destructive actions
- Clear warning messages
- Exit on errors

### ✅ Health Monitoring
- Backend health endpoint check
- Frontend availability check
- JSON formatted output

## Examples

### Complete First-Time Setup
```bash
# Install Docker (if not installed)
./build.sh install-docker

# Setup project
./build.sh setup

# Access applications
# Frontend: http://localhost:4200
# Backend: http://localhost:8000
```

### Build and Monitor
```bash
# Build
./build.sh build

# Start
./build.sh start

# Check health
./build.sh health

# View backend logs
./build.sh logs-backend
```

### Backup Data Before Clean
```bash
# Backup data
./build.sh backup

# Clean up
./build.sh clean-all

# Restore from backup if needed
# (backup files in ./backups/ directory)
```

## Troubleshooting

### Permission Denied
```bash
# Make script executable
chmod +x build.sh

# Or run with bash
bash build.sh build
```

### Docker Not Running
```bash
# Start Docker
sudo systemctl start docker

# Or install Docker
./build.sh install-docker
```

### Port Already in Use
```bash
# Check what's using ports
sudo lsof -i :8000
sudo lsof -i :4200

# Stop services
./build.sh stop

# Try again
./build.sh start
```

### Build Fails
```bash
# Clean everything
./build.sh clean

# Rebuild without cache
./build.sh rebuild
```

## Script Help

```bash
# Show all commands
./build.sh help

# Or just run without arguments
./build.sh
```

## Output Example

```bash
$ ./build.sh build
==> Building all Docker images...
[+] Building 1024.5s (20/20) FINISHED
==> Build complete!

$ ./build.sh start
==> Starting services...
==> Services started!

Frontend: http://localhost:4200
Backend:  http://localhost:8000
API Docs: http://localhost:8000/docs

$ ./build.sh health
==> Checking service health...

Backend:  ✓ Healthy
{
  "status": "healthy",
  "message": "Service is operational"
}

Frontend: ✓ Healthy (HTTP 200)
```

## Script Location

The script is located at:
```
./build.sh
```

Keep it in the root of your AI Teacher project directory.

---

**Quick Reference:**
- First time: `chmod +x build.sh && ./build.sh setup`
- Build: `./build.sh build`
- Start: `./build.sh start`
- Logs: `./build.sh logs`
- Stop: `./build.sh stop`
- Help: `./build.sh help`
