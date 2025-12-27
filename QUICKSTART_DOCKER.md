# Docker Quick Start Guide

## Ultra-Quick Start (Ubuntu/Linux)

**Just run ONE command:**
```bash
chmod +x build.sh && ./build.sh
```

That's it! The script will:
1. Check if Docker is installed (install if needed)
2. Create .env file
3. Build Docker images
4. Start all services
5. Show you the access URLs

## Ultra-Quick Start (Windows)

**Just double-click or run:**
```cmd
build.bat
```

Then follow the prompts!

---

## What Happens When You Run build.sh (No Parameters)

```bash
$ ./build.sh

INFO: No command specified, running setup...

==> Setting up AI Teacher...

==> Checking Docker installation...

==> Docker is installed
Docker version 24.0.6

==> Docker Compose is available
Docker Compose version v2.23.0

==> Docker daemon is running

[SUCCESS] Docker is properly configured and running!

==> .env file exists

==> Building Docker images (this may take 15-20 minutes first time)...
[Building...]

==> Starting services...

=========================================
==> Setup complete!
=========================================

Frontend: http://localhost:4200
Backend:  http://localhost:8000
API Docs: http://localhost:8000/docs

INFO: Run './build.sh logs' to view logs
INFO: Run './build.sh status' to check status
```

---

## Available Commands (Optional)

You can still use all commands if you want more control:

### Ubuntu/Linux
```bash
./build.sh                  # Run setup (default)
./build.sh help             # Show help
./build.sh check-docker     # Check Docker
./build.sh install-docker   # Install Docker
./build.sh build            # Build only
./build.sh start            # Start only
./build.sh logs             # View logs
./build.sh stop             # Stop services
```

### Windows
```cmd
build.bat                   # Show help menu
build.bat setup             # Run setup
build.bat check-docker      # Check Docker
build.bat install-docker    # Install Docker
build.bat build             # Build only
build.bat up                # Start only
build.bat logs              # View logs
build.bat down              # Stop services
```

---

## What If Docker Is Not Installed?

### Linux
```bash
$ ./build.sh

INFO: No command specified, running setup...

==> Setting up AI Teacher...

ERROR: Docker is NOT installed!

Docker is required to run this application.

To install Docker:
  1. Run: ./build.sh install-docker
  2. Or follow manual instructions

# Then run the installer
$ ./build.sh install-docker
[Installs Docker automatically]

# Run setup again
$ ./build.sh
```

### Windows
```cmd
C:\AI_teacher> build.bat

# Shows help menu
# Run check
C:\AI_teacher> build.bat check-docker

[ERROR] Docker is NOT installed!
To install Docker:
  1. Run: build.bat install-docker

# Run installer
C:\AI_teacher> build.bat install-docker
[Downloads and installs Docker Desktop]

# Restart computer, start Docker Desktop, then:
C:\AI_teacher> build.bat setup
```

---

## Complete First-Time Workflow

### Linux (Ubuntu)
```bash
# Step 1: Make executable and run
cd /path/to/AI_teacher
chmod +x build.sh
./build.sh

# That's it! If Docker isn't installed, it will guide you.
```

### Windows
```cmd
# Step 1: Open Command Prompt in project folder
cd C:\path\to\AI_teacher

# Step 2: Run setup
build.bat setup

# That's it! If Docker isn't installed, it will guide you.
```

---

## Access Your Application

After setup completes, access:

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Common Tasks

### View Logs
```bash
# Linux
./build.sh logs
./build.sh logs-backend

# Windows
build.bat logs
build.bat logs-backend
```

### Stop Services
```bash
# Linux
./build.sh stop

# Windows
build.bat down
```

### Rebuild After Code Changes
```bash
# Linux
./build.sh build
./build.sh restart

# Windows
build.bat build
build.bat restart
```

### Check Status
```bash
# Linux
./build.sh status

# Windows
build.bat ps
```

---

## Troubleshooting

### "Docker not running"
**Linux:**
```bash
sudo systemctl start docker
./build.sh check-docker
```

**Windows:**
- Start "Docker Desktop" from Start Menu
- Wait for whale icon in system tray to be ready

### "Permission denied" (Linux)
```bash
sudo usermod -aG docker $USER
# Log out and back in, or:
newgrp docker
```

### "Build failed"
```bash
# Linux
./build.sh clean
./build.sh rebuild

# Windows
build.bat clean
build.bat rebuild
```

---

## Summary

**You don't need to remember any commands!**

**Linux:** Just run `./build.sh`

**Windows:** Just run `build.bat setup`

Everything else is automatic! 🚀

---

## Need More Details?

See comprehensive guides:
- `BUILD_SCRIPT_GUIDE.md` - Complete script documentation
- `docs/DOCKER_BUILD_OPTIMIZATION.md` - Technical details
- `docs/DOCKER_QUICK_REFERENCE.md` - Command reference

---

**Made easy for developers! Just one command to get started.** ✨
