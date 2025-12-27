@echo off
REM AI Teacher - Windows Build Script with Docker Installation Check
REM Enhanced version with automatic Docker detection and installation guidance

setlocal enabledelayedexpansion

REM Colors using PowerShell for better output
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM If no parameters, run setup automatically
if "%1"=="" (
    echo [INFO] No command specified, running setup...
    echo.
    goto setup
)

if "%1"=="help" goto help
if "%1"=="check-docker" goto check_docker
if "%1"=="install-docker" goto install_docker
if "%1"=="setup" goto setup
if "%1"=="build" goto build
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="logs-backend" goto logs_backend
if "%1"=="logs-frontend" goto logs_frontend
if "%1"=="ps" goto ps
if "%1"=="clean" goto clean
if "%1"=="rebuild" goto rebuild
goto help

:help
echo ========================================
echo AI Teacher - Docker Commands for Windows
echo ========================================
echo.
echo Quick Start:
echo   build.bat              - Run setup automatically (no parameters needed!)
echo.
echo Prerequisites:
echo   build.bat check-docker    - Check if Docker is installed
echo   build.bat install-docker  - Install Docker Desktop for Windows
echo.
echo Setup:
echo   build.bat setup           - Initial setup (copy .env, build, start)
echo   build.bat build           - Build Docker images
echo.
echo Running:
echo   build.bat up              - Start all services
echo   build.bat down            - Stop all services
echo   build.bat restart         - Restart all services
echo.
echo Monitoring:
echo   build.bat logs            - View logs (all services)
echo   build.bat logs-backend    - View backend logs only
echo   build.bat logs-frontend   - View frontend logs only
echo   build.bat ps              - Show running containers
echo.
echo Maintenance:
echo   build.bat clean           - Remove containers and images
echo   build.bat rebuild         - Rebuild and restart (no cache)
echo.
echo TIP: Just run 'build.bat' without parameters to do everything!
echo.
goto end

:check_docker
echo.
echo Checking Docker installation...
echo.

REM Check if docker command exists
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is NOT installed!
    echo.
    echo Docker Desktop for Windows is required to run this application.
    echo.
    echo To install Docker:
    echo   1. Run: build.bat install-docker
    echo   2. Or manually download from: https://www.docker.com/products/docker-desktop
    echo.
    exit /b 1
) else (
    echo [OK] Docker is installed
    docker --version
)

echo.

REM Check if docker compose is available
docker compose version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is NOT available!
    echo.
    echo Docker Compose should come with Docker Desktop.
    echo Please reinstall Docker Desktop for Windows.
    echo.
    exit /b 1
) else (
    echo [OK] Docker Compose is available
    docker compose version
)

echo.

REM Check if Docker daemon is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker daemon is NOT running!
    echo.
    echo Please start Docker Desktop application.
    echo Look for Docker icon in system tray (bottom-right).
    echo.
    exit /b 1
) else (
    echo [OK] Docker daemon is running
)

echo.
echo [SUCCESS] Docker is properly configured and running!
echo.
goto end

:install_docker
echo.
echo ========================================
echo Docker Desktop Installation for Windows
echo ========================================
echo.
echo This script will help you install Docker Desktop for Windows.
echo.

REM Check if already installed
docker --version >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Docker is already installed!
    docker --version
    echo.
    set /p "reinstall=Do you want to reinstall? (y/N): "
    if /i not "!reinstall!"=="y" (
        echo Installation cancelled.
        goto end
    )
)

echo.
echo System Requirements:
echo   - Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
echo   - OR Windows 11 64-bit
echo   - WSL 2 feature enabled
echo   - 4GB RAM minimum
echo.

set /p "continue=Do you want to continue with Docker installation? (Y/n): "
if /i "!continue!"=="n" (
    echo Installation cancelled.
    goto end
)

echo.
echo Step 1: Checking Windows version...
ver | findstr /i "10\.0\." >nul
if errorlevel 1 (
    echo [WARNING] Could not verify Windows version.
    echo Please ensure you have Windows 10/11.
) else (
    echo [OK] Windows version compatible
)

echo.
echo Step 2: Downloading Docker Desktop installer...
echo.
echo Opening download page in your browser...
echo URL: https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe
echo.

REM Try to download using PowerShell
echo Attempting to download Docker Desktop installer...
powershell -Command "& {try { $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://desktop.docker.com/win/stable/Docker%%20Desktop%%20Installer.exe' -OutFile '%TEMP%\DockerDesktopInstaller.exe' -UseBasicParsing; Write-Host '[OK] Download completed!' } catch { Write-Host '[ERROR] Download failed. Please download manually.' }}"

if exist "%TEMP%\DockerDesktopInstaller.exe" (
    echo.
    echo [SUCCESS] Installer downloaded to: %TEMP%\DockerDesktopInstaller.exe
    echo.
    set /p "install_now=Do you want to run the installer now? (Y/n): "
    if /i not "!install_now!"=="n" (
        echo.
        echo Starting Docker Desktop installer...
        echo Please follow the installation wizard.
        echo.
        echo IMPORTANT:
        echo   1. Accept the license agreement
        echo   2. Ensure "Use WSL 2 instead of Hyper-V" is checked (recommended)
        echo   3. Complete the installation
        echo   4. RESTART YOUR COMPUTER when prompted
        echo.
        start "" "%TEMP%\DockerDesktopInstaller.exe"
        echo.
        echo After installation and restart:
        echo   1. Start Docker Desktop from Start Menu
        echo   2. Wait for Docker to start (check system tray icon)
        echo   3. Run: build.bat check-docker
        echo.
    ) else (
        echo.
        echo Installer ready at: %TEMP%\DockerDesktopInstaller.exe
        echo Run it when you're ready to install Docker Desktop.
    )
) else (
    echo.
    echo [INFO] Automatic download not available.
    echo.
    echo Please install Docker Desktop manually:
    echo.
    echo 1. Visit: https://www.docker.com/products/docker-desktop
    echo 2. Click "Download for Windows"
    echo 3. Run the installer (DockerDesktopInstaller.exe)
    echo 4. Follow the installation wizard
    echo 5. Restart your computer when prompted
    echo 6. Start Docker Desktop
    echo 7. Run: build.bat check-docker
    echo.
    echo Opening download page in browser...
    start https://www.docker.com/products/docker-desktop
)

echo.
echo Installation guide complete!
echo.
goto end

:setup
echo.
echo Setting up AI Teacher...
echo.

REM Check Docker first
call :check_docker
if errorlevel 1 (
    echo.
    echo [ERROR] Docker is not properly configured.
    echo Please run: build.bat install-docker
    echo.
    exit /b 1
)

echo.
REM Check for .env file
if not exist .env (
    echo Creating .env file from .env.example...
    if not exist .env.example (
        echo [ERROR] .env.example not found!
        echo Please ensure you're in the correct directory.
        exit /b 1
    )
    copy .env.example .env
    echo.
    echo [ACTION REQUIRED] Please edit .env file with your API keys:
    echo   - OPENAI_API_KEY
    echo   - EXA_API_KEY
    echo.
    echo Opening .env file in Notepad...
    start notepad .env
    echo.
    echo After saving your API keys, run: build.bat setup
    echo.
    exit /b 1
) else (
    echo [OK] .env file exists
)

echo.
echo Building Docker images (this may take 15-20 minutes first time)...
docker compose build
if errorlevel 1 (
    echo [ERROR] Build failed!
    exit /b 1
)

echo.
echo Starting services...
docker compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services!
    exit /b 1
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Frontend: http://localhost:4200
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Run 'build.bat logs' to view logs
echo Run 'build.bat ps' to check status
echo.
goto end

:build
call :check_docker_quick
echo Building Docker images...
docker compose build
if errorlevel 1 (
    echo [ERROR] Build failed!
    exit /b 1
)
echo [OK] Build complete!
goto end

:rebuild
call :check_docker_quick
echo Rebuilding without cache...
docker compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Rebuild failed!
    exit /b 1
)
echo Starting services...
docker compose up -d
echo [OK] Rebuild complete!
goto end

:up
call :check_docker_quick
echo Starting services...
docker compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services!
    exit /b 1
)
echo.
echo Services started!
echo Frontend: http://localhost:4200
echo Backend:  http://localhost:8000/docs
goto end

:down
call :check_docker_quick
echo Stopping services...
docker compose down
echo Services stopped!
goto end

:restart
call :check_docker_quick
echo Restarting services...
docker compose restart
echo Services restarted!
goto end

:logs
call :check_docker_quick
echo Viewing logs (Press Ctrl+C to exit)...
docker compose logs -f
goto end

:logs_backend
call :check_docker_quick
echo Viewing backend logs (Press Ctrl+C to exit)...
docker compose logs -f backend
goto end

:logs_frontend
call :check_docker_quick
echo Viewing frontend logs (Press Ctrl+C to exit)...
docker compose logs -f frontend
goto end

:ps
call :check_docker_quick
echo Container status:
echo.
docker compose ps
goto end

:clean
call :check_docker_quick
echo Removing containers and images...
set /p "confirm=Are you sure? (y/N): "
if /i "!confirm!"=="y" (
    docker compose down
    docker compose rm -f
    docker image prune -f
    echo Cleanup complete!
) else (
    echo Cancelled.
)
goto end

REM Quick Docker check (no output unless error)
:check_docker_quick
docker ps >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Docker is not running!
    echo.
    echo Please:
    echo   1. Start Docker Desktop application
    echo   2. Wait for it to be ready (check system tray)
    echo   3. Run: build.bat check-docker
    echo.
    exit /b 1
)
exit /b 0

:end
endlocal
