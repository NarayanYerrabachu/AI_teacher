@echo off
REM AI Teacher - Windows Build Script
REM Equivalent to Makefile commands for Windows users

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="build" goto build
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="logs-backend" goto logs-backend
if "%1"=="logs-frontend" goto logs-frontend
if "%1"=="ps" goto ps
if "%1"=="clean" goto clean
if "%1"=="rebuild" goto rebuild
goto help

:help
echo AI Teacher - Docker Commands for Windows
echo ==========================================
echo.
echo Setup:
echo   build.bat setup       - Initial setup (copy .env, build, start)
echo   build.bat build       - Build Docker images
echo.
echo Running:
echo   build.bat up          - Start all services
echo   build.bat down        - Stop all services
echo   build.bat restart     - Restart all services
echo.
echo Monitoring:
echo   build.bat logs        - View logs (all services)
echo   build.bat logs-backend  - View backend logs only
echo   build.bat logs-frontend - View frontend logs only
echo   build.bat ps          - Show running containers
echo.
echo Maintenance:
echo   build.bat clean       - Remove containers and images
echo   build.bat rebuild     - Rebuild and restart (no cache)
echo.
goto end

:setup
echo Setting up AI Teacher...
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Please edit .env file with your API keys
    exit /b 1
)
echo Building Docker images...
docker compose build
echo Starting services...
docker compose up -d
echo.
echo Setup complete!
echo Frontend: http://localhost:4200
echo Backend: http://localhost:8000/docs
goto end

:build
echo Building Docker images...
docker compose build
goto end

:rebuild
echo Rebuilding without cache...
docker compose build --no-cache
docker compose up -d
goto end

:up
echo Starting services...
docker compose up -d
echo Services started!
echo Frontend: http://localhost:4200
echo Backend: http://localhost:8000/docs
goto end

:down
echo Stopping services...
docker compose down
goto end

:restart
echo Restarting services...
docker compose restart
goto end

:logs
echo Viewing logs (all services)...
docker compose logs -f
goto end

:logs-backend
echo Viewing backend logs...
docker compose logs -f backend
goto end

:logs-frontend
echo Viewing frontend logs...
docker compose logs -f frontend
goto end

:ps
echo Showing container status...
docker compose ps
goto end

:clean
echo Removing containers and images...
docker compose down
docker compose rm -f
docker image prune -f
goto end

:end
