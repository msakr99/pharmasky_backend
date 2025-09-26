#!/bin/bash

# PharmasSky GitHub-based Deployment Script for DigitalOcean
# This script deploys the Django application directly from GitHub repository

set -e  # Exit on any error

echo "🚀 Starting PharmasSky GitHub-based deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/pharmasky"
BACKUP_DIR="/opt/backups"
LOG_FILE="/var/log/pharmasky-deploy.log"
GITHUB_REPO="https://github.com/msakr99/pharmasky_backend.git"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check and install docker if needed
    if ! command_exists docker; then
        print_status "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
    fi
    
    # Check and install docker-compose if needed
    if ! command_exists docker-compose; then
        print_status "Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    # Check and install git if needed
    if ! command_exists git; then
        print_status "Installing Git..."
        apt update && apt install -y git
    fi
    
    print_success "All prerequisites are satisfied."
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p $PROJECT_DIR
    mkdir -p $BACKUP_DIR
    mkdir -p $(dirname $LOG_FILE)
    print_success "Directories created."
}

# Update system and install dependencies
install_system_dependencies() {
    print_status "Updating system and installing dependencies..."
    apt update
    apt install -y curl wget git nginx certbot python3-certbot-nginx ufw
    print_success "System dependencies installed."
}

# Configure firewall
configure_firewall() {
    print_status "Configuring UFW firewall..."
    ufw --force enable
    ufw allow ssh
    ufw allow 80
    ufw allow 443
    print_success "Firewall configured."
}

# Clone or update repository from GitHub
setup_repository() {
    print_status "Setting up repository from GitHub..."
    
    if [ -d "$PROJECT_DIR/.git" ]; then
        print_status "Repository exists, pulling latest changes from GitHub..."
        cd $PROJECT_DIR
        git fetch origin
        git reset --hard origin/main
    else
        print_status "Cloning repository from GitHub..."
        git clone $GITHUB_REPO $PROJECT_DIR
        cd $PROJECT_DIR
    fi
    
    # Set proper permissions
    chmod +x deploy.sh || true
    chmod +x manage_deployment.sh || true
    chmod +x github_deploy.sh || true
    
    print_success "Repository setup complete."
}

# Setup environment file
setup_environment() {
    print_status "Setting up environment file..."
    
    cd $PROJECT_DIR
    
    if [ ! -f ".env.production" ]; then
        if [ -f "production.env" ]; then
            cp production.env .env.production
            print_warning "Created .env.production from production.env template"
            print_warning "Please edit .env.production with your actual values:"
            print_warning "1. Update ALLOWED_HOSTS with your domain/IP"
            print_warning "2. Set a secure SECRET_KEY"
            print_warning "3. Configure DigitalOcean Spaces credentials"
        else
            print_error "No environment template found!"
            exit 1
        fi
    fi
    
    print_success "Environment file setup complete."
}

# Build and start containers
deploy_containers() {
    print_status "Building and starting Docker containers..."
    
    cd $PROJECT_DIR
    
    # Stop existing containers
    if [ "$(docker-compose ps -q)" ]; then
        print_status "Stopping existing containers..."
        docker-compose down
    fi
    
    # Build and start new deployment
    docker-compose build --no-cache
    docker-compose up -d
    
    print_success "Containers deployed successfully."
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    cd $PROJECT_DIR
    
    # Wait for database to be ready
    sleep 30
    
    docker-compose exec -T web python manage.py migrate
    print_success "Database migrations completed."
}

# Collect static files
collect_static() {
    print_status "Collecting static files..."
    cd $PROJECT_DIR
    docker-compose exec -T web python manage.py collectstatic --noinput
    print_success "Static files collected."
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Wait for services to be fully ready
    sleep 10
    
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Health check attempt $attempt of $max_attempts..."
        
        if curl -f -s http://localhost/health/ > /dev/null 2>&1; then
            print_success "Health check passed!"
            return 0
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "Health check failed after $max_attempts attempts"
            return 1
        fi
        
        sleep 15
        attempt=$((attempt + 1))
    done
}

# Main deployment function
main() {
    print_status "Starting PharmasSky GitHub-based deployment process..."
    
    check_prerequisites
    create_directories
    install_system_dependencies
    configure_firewall
    setup_repository
    setup_environment
    deploy_containers
    run_migrations
    collect_static
    health_check
    
    print_success "🎉 Deployment completed successfully!"
    print_status "Your application should be available at:"
    print_status "- HTTP: http://$(curl -s ifconfig.me 2>/dev/null || echo 'your-droplet-ip')"
    print_status "- Admin: http://$(curl -s ifconfig.me 2>/dev/null || echo 'your-droplet-ip')/admin/"
    
    print_status "Next steps:"
    print_status "1. Create a superuser: docker-compose exec web python manage.py createsuperuser"
    print_status "2. Update .env.production with your domain name"
    print_status "3. Setup SSL certificate if you have a domain"
    
    print_status "Useful commands:"
    print_status "- View logs: docker-compose logs -f"
    print_status "- Restart services: docker-compose restart"
    print_status "- Update from GitHub: cd /opt/pharmasky && git pull && docker-compose up --build -d"
}

# Run main function
main 2>&1 | tee -a $LOG_FILE
