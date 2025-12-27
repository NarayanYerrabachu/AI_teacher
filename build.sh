#!/bin/bash
# AI Teacher - Ubuntu Linux Build Script
# Comprehensive Docker management script

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${GREEN}==>${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

print_info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

# Show help
show_help() {
    echo -e "${BLUE}AI Teacher - Docker Build Script for Ubuntu Linux${NC}"
    echo "=================================================="
    echo ""
    echo "Usage: ./build.sh [command]"
    echo ""
    echo -e "${GREEN}Quick Start:${NC}"
    echo "  ./build.sh              - Run setup automatically (no parameters needed!)"
    echo ""
    echo "Prerequisites:"
    echo "  check-docker    - Check if Docker is installed and running"
    echo "  install-docker  - Install Docker on Ubuntu (requires sudo)"
    echo ""
    echo "Setup Commands:"
    echo "  setup           - Initial setup (copy .env, build, start)"
    echo ""
    echo "Build Commands:"
    echo "  build           - Build all Docker images"
    echo "  build-backend   - Build backend only"
    echo "  build-frontend  - Build frontend only"
    echo "  rebuild         - Rebuild without cache"
    echo ""
    echo "Service Management:"
    echo "  start           - Start all services"
    echo "  stop            - Stop all services"
    echo "  restart         - Restart all services"
    echo "  status          - Show container status"
    echo ""
    echo "Monitoring:"
    echo "  logs            - View all logs"
    echo "  logs-backend    - View backend logs"
    echo "  logs-frontend   - View frontend logs"
    echo "  stats           - Show resource usage"
    echo "  health          - Check service health"
    echo ""
    echo "Maintenance:"
    echo "  clean           - Remove containers and images"
    echo "  clean-all       - Remove everything (including volumes)"
    echo "  prune           - Clean up Docker system"
    echo "  backup          - Backup data volumes"
    echo ""
    echo "Shell Access:"
    echo "  shell-backend   - Access backend container shell"
    echo "  shell-frontend  - Access frontend container shell"
    echo ""
    echo "Examples:"
    echo "  ./build.sh                    # Run setup (automatic!)"
    echo "  ./build.sh help               # Show this help"
    echo "  ./build.sh build              # Build images only"
    echo "  ./build.sh logs-backend       # View backend logs"
    echo ""
    echo -e "${GREEN}TIP:${NC} Just run './build.sh' without parameters to do everything!"
    echo ""
}

# Check if Docker is installed (detailed check)
check_docker_detailed() {
    echo ""
    print_msg "Checking Docker installation..."
    echo ""

    # Check if docker command exists
    if ! command -v docker &> /dev/null; then
        print_error "Docker is NOT installed!"
        echo ""
        echo "Docker is required to run this application."
        echo ""
        echo "To install Docker:"
        echo "  1. Run: ./build.sh install-docker"
        echo "  2. Or follow manual instructions at: https://docs.docker.com/engine/install/ubuntu/"
        echo ""
        return 1
    else
        print_msg "Docker is installed"
        docker --version
    fi

    echo ""

    # Check if docker compose is available
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is NOT available!"
        echo ""
        echo "Docker Compose should come with Docker."
        echo "Please reinstall Docker or install docker-compose-plugin."
        echo ""
        echo "Run: sudo apt install docker-compose-plugin"
        echo ""
        return 1
    else
        print_msg "Docker Compose is available"
        docker compose version
    fi

    echo ""

    # Check if Docker daemon is running
    if ! docker ps &> /dev/null; then
        print_error "Docker daemon is NOT running or permission denied!"
        echo ""
        echo "Please:"
        echo "  1. Start Docker: sudo systemctl start docker"
        echo "  2. Or add user to docker group: sudo usermod -aG docker \$USER"
        echo "  3. Then log out and back in (or run: newgrp docker)"
        echo ""
        return 1
    else
        print_msg "Docker daemon is running"
    fi

    echo ""
    echo -e "${GREEN}[SUCCESS]${NC} Docker is properly configured and running!"
    echo ""
    return 0
}

# Quick Docker check (silent unless error)
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Run: ./build.sh install-docker"
        exit 1
    fi

    if ! docker ps &> /dev/null; then
        print_error "Docker daemon is not running or you don't have permission"
        echo ""
        echo "Please:"
        echo "  1. Start Docker: sudo systemctl start docker"
        echo "  2. Or add user to docker group: sudo usermod -aG docker \$USER"
        echo "  3. Run: ./build.sh check-docker"
        echo ""
        exit 1
    fi
}

# Install Docker on Ubuntu
install_docker() {
    echo ""
    print_msg "Docker Installation for Ubuntu Linux"
    echo "====================================="
    echo ""

    # Check if already installed
    if command -v docker &> /dev/null; then
        print_warning "Docker is already installed!"
        docker --version
        echo ""
        read -p "Do you want to reinstall? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Installation cancelled"
            exit 0
        fi
    fi

    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_warning "Please run this script as a regular user, not as root"
        print_info "The script will request sudo permission when needed"
        exit 1
    fi

    echo ""
    print_msg "This will install Docker Engine and Docker Compose on Ubuntu"
    echo ""
    echo "Steps:"
    echo "  1. Update package index"
    echo "  2. Install Docker and Docker Compose"
    echo "  3. Add user to docker group"
    echo "  4. Enable and start Docker service"
    echo ""
    read -p "Continue with installation? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi

    echo ""
    print_msg "Step 1: Updating package index..."
    sudo apt update

    echo ""
    print_msg "Step 2: Installing Docker and Docker Compose..."
    sudo apt install -y docker.io docker-compose-plugin

    if [ $? -ne 0 ]; then
        print_error "Docker installation failed!"
        echo ""
        print_info "Try manual installation:"
        echo "  https://docs.docker.com/engine/install/ubuntu/"
        exit 1
    fi

    echo ""
    print_msg "Step 3: Adding user '$USER' to docker group..."
    sudo usermod -aG docker $USER

    echo ""
    print_msg "Step 4: Enabling and starting Docker service..."
    sudo systemctl enable docker
    sudo systemctl start docker

    echo ""
    echo "====================================="
    print_msg "Docker installed successfully!"
    echo "====================================="
    echo ""
    docker --version
    docker compose version
    echo ""

    print_warning "IMPORTANT: You must log out and back in for group changes to take effect!"
    echo ""
    print_info "Quick option: Run 'newgrp docker' to activate group in current session"
    print_info "Then run: ./build.sh check-docker"
    echo ""
}

# Setup environment
setup_env() {
    echo ""
    print_msg "Setting up AI Teacher..."
    echo ""

    # Check Docker first
    if ! check_docker_detailed; then
        echo ""
        print_error "Docker is not properly configured"
        print_info "Run: ./build.sh install-docker"
        echo ""
        exit 1
    fi

    echo ""
    # Check for .env file
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            print_msg "Creating .env file from .env.example..."
            cp .env.example .env
            echo ""
            print_warning "Please edit .env file with your API keys:"
            print_info "  nano .env"
            print_info "  Required: OPENAI_API_KEY, EXA_API_KEY"
            echo ""
            print_info "After saving your API keys, run: ./build.sh setup"
            echo ""
            exit 1
        else
            print_error ".env.example not found!"
            exit 1
        fi
    else
        print_msg ".env file exists"
    fi

    echo ""
    # Build images
    print_msg "Building Docker images (this may take 15-20 minutes first time)..."
    docker compose build

    if [ $? -ne 0 ]; then
        print_error "Build failed!"
        exit 1
    fi

    echo ""
    # Start services
    print_msg "Starting services..."
    docker compose up -d

    if [ $? -ne 0 ]; then
        print_error "Failed to start services!"
        exit 1
    fi

    # Wait for services to be healthy
    print_msg "Waiting for services to be ready..."
    sleep 10

    # Show status
    echo ""
    echo "========================================="
    print_msg "Setup complete!"
    echo "========================================="
    echo ""
    echo -e "${GREEN}Frontend:${NC} http://localhost:4200"
    echo -e "${GREEN}Backend:${NC}  http://localhost:8000"
    echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
    echo ""
    print_info "Run './build.sh logs' to view logs"
    print_info "Run './build.sh status' to check status"
    echo ""
}

# Build all images
build_all() {
    check_docker
    print_msg "Building all Docker images..."
    docker compose build
    print_msg "Build complete!"
}

# Build backend only
build_backend() {
    check_docker
    print_msg "Building backend image..."
    docker compose build backend
    print_msg "Backend build complete!"
}

# Build frontend only
build_frontend() {
    check_docker
    print_msg "Building frontend image..."
    docker compose build frontend
    print_msg "Frontend build complete!"
}

# Rebuild without cache
rebuild_all() {
    check_docker
    print_msg "Rebuilding all images without cache..."
    docker compose build --no-cache
    print_msg "Rebuild complete!"
}

# Start services
start_services() {
    check_docker
    print_msg "Starting services..."
    docker compose up -d

    sleep 3
    print_msg "Services started!"
    echo ""
    echo -e "${GREEN}Frontend:${NC} http://localhost:4200"
    echo -e "${GREEN}Backend:${NC}  http://localhost:8000"
    echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
}

# Stop services
stop_services() {
    check_docker
    print_msg "Stopping services..."
    docker compose down
    print_msg "Services stopped!"
}

# Restart services
restart_services() {
    check_docker
    print_msg "Restarting services..."
    docker compose restart
    print_msg "Services restarted!"
}

# Show status
show_status() {
    check_docker
    print_msg "Container status:"
    echo ""
    docker compose ps
    echo ""
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# View all logs
view_logs() {
    check_docker
    print_msg "Viewing logs (Press Ctrl+C to exit)..."
    docker compose logs -f
}

# View backend logs
view_logs_backend() {
    check_docker
    print_msg "Viewing backend logs (Press Ctrl+C to exit)..."
    docker compose logs -f backend
}

# View frontend logs
view_logs_frontend() {
    check_docker
    print_msg "Viewing frontend logs (Press Ctrl+C to exit)..."
    docker compose logs -f frontend
}

# Show resource stats
show_stats() {
    check_docker
    print_msg "Resource usage (Press Ctrl+C to exit)..."
    docker stats
}

# Health check
health_check() {
    check_docker
    print_msg "Checking service health..."
    echo ""

    # Backend health
    echo -n "Backend:  "
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo ""
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi

    echo ""

    # Frontend health
    echo -n "Frontend: "
    if curl -s -f -o /dev/null http://localhost:4200/; then
        echo -e "${GREEN}✓ Healthy${NC} (HTTP 200)"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
}

# Clean up containers and images
clean_up() {
    check_docker
    print_warning "This will remove containers and images"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_msg "Cleaning up..."
        docker compose down
        docker compose rm -f
        docker image prune -f
        print_msg "Cleanup complete!"
    else
        print_info "Cancelled"
    fi
}

# Clean everything including volumes
clean_all() {
    check_docker
    print_error "WARNING: This will remove ALL data including volumes!"
    print_warning "Your ChromaDB data and uploads will be deleted!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_msg "Removing everything..."
        docker compose down -v
        docker image prune -a -f
        docker volume prune -f
        print_msg "Everything removed!"
    else
        print_info "Cancelled"
    fi
}

# Prune Docker system
prune_system() {
    check_docker
    print_msg "Cleaning up Docker system..."
    docker system prune -a
    print_msg "System cleanup complete!"
}

# Backup data volumes
backup_volumes() {
    check_docker
    print_msg "Backing up data volumes..."

    mkdir -p backups
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)

    # Backup ChromaDB
    print_msg "Backing up ChromaDB..."
    docker run --rm \
        -v ai_teacher_chroma_data:/data \
        -v $(pwd)/backups:/backup \
        alpine tar czf /backup/chroma_${TIMESTAMP}.tar.gz /data

    # Backup uploads
    print_msg "Backing up uploads..."
    docker run --rm \
        -v ai_teacher_uploads_data:/data \
        -v $(pwd)/backups:/backup \
        alpine tar czf /backup/uploads_${TIMESTAMP}.tar.gz /data

    print_msg "Backup complete!"
    ls -lh backups/
}

# Access backend shell
shell_backend() {
    check_docker
    print_msg "Accessing backend container shell..."
    docker compose exec backend bash
}

# Access frontend shell
shell_frontend() {
    check_docker
    print_msg "Accessing frontend container shell..."
    docker compose exec frontend sh
}

# Main script logic
# If no parameters provided, run setup by default
if [ $# -eq 0 ]; then
    print_info "No command specified, running setup..."
    echo ""
    setup_env
    exit 0
fi

case "${1}" in
    help|--help|-h)
        show_help
        ;;
    check-docker)
        check_docker_detailed
        ;;
    install-docker)
        install_docker
        ;;
    setup)
        setup_env
        ;;
    build)
        build_all
        ;;
    build-backend)
        build_backend
        ;;
    build-frontend)
        build_frontend
        ;;
    rebuild)
        rebuild_all
        ;;
    start|up)
        start_services
        ;;
    stop|down)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status|ps)
        show_status
        ;;
    logs)
        view_logs
        ;;
    logs-backend)
        view_logs_backend
        ;;
    logs-frontend)
        view_logs_frontend
        ;;
    stats)
        show_stats
        ;;
    health)
        health_check
        ;;
    clean)
        clean_up
        ;;
    clean-all)
        clean_all
        ;;
    prune)
        prune_system
        ;;
    backup)
        backup_volumes
        ;;
    shell-backend)
        shell_backend
        ;;
    shell-frontend)
        shell_frontend
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

exit 0
