#!/bin/bash

# PharmaScope Deployment Script for DigitalOcean
# This script deploys the Django application using Docker

set -e  # Exit on any error

echo "🚀 Starting PharmaScope deployment..."

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
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if ! command_exists git; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_success "All prerequisites are satisfied."
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    sudo mkdir -p $PROJECT_DIR
    sudo mkdir -p $BACKUP_DIR
    sudo mkdir -p $(dirname $LOG_FILE)
    print_success "Directories created."
}

# Update system and install dependencies
install_system_dependencies() {
    print_status "Updating system and installing dependencies..."
    sudo apt update
    sudo apt install -y curl wget git nginx certbot python3-certbot-nginx ufw
    print_success "System dependencies installed."
}

# Configure firewall
configure_firewall() {
    print_status "Configuring UFW firewall..."
    sudo ufw --force enable
    sudo ufw allow ssh
    sudo ufw allow 80
    sudo ufw allow 443
    print_success "Firewall configured."
}

# Clone or update repository
setup_repository() {
    print_status "Setting up repository..."
    
    if [ -d "$PROJECT_DIR/.git" ]; then
        print_status "Repository exists, pulling latest changes..."
        cd $PROJECT_DIR
        sudo git fetch origin
        sudo git reset --hard origin/main
    else
        print_status "Cloning repository..."
        sudo git clone https://github.com/msakr99/pharmasky_backend.git $PROJECT_DIR
        cd $PROJECT_DIR
    fi
    
    # Set proper permissions
    sudo chown -R root:root $PROJECT_DIR
    sudo chmod +x $PROJECT_DIR/deploy.sh
    sudo chmod +x $PROJECT_DIR/manage_deployment.sh
    
    print_success "Repository setup complete."
}

# Setup environment file
setup_environment() {
    print_status "Setting up environment file..."
    
    if [ ! -f "$PROJECT_DIR/.env.production" ]; then
        sudo cp $PROJECT_DIR/production.env $PROJECT_DIR/.env.production
        print_warning "Please edit .env.production with your actual values before continuing."
        print_warning "Run: sudo nano $PROJECT_DIR/.env.production"
        read -p "Press enter to continue after editing the environment file..."
    fi
    
    print_success "Environment file setup complete."
}

# Build and start containers
deploy_containers() {
    print_status "Building and starting Docker containers..."
    
    cd $PROJECT_DIR
    
    # Create backup of current deployment if it exists
    if [ "$(sudo docker ps -q)" ]; then
        print_status "Creating backup of current deployment..."
        sudo docker-compose down
        sudo mkdir -p $BACKUP_DIR/$(date +%Y%m%d_%H%M%S)
    fi
    
    # Build and start new deployment
    sudo docker-compose build --no-cache
    sudo docker-compose up -d
    
    print_success "Containers deployed successfully."
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    sudo docker-compose exec web python manage.py migrate
    print_success "Database migrations completed."
}

# Collect static files
collect_static() {
    print_status "Collecting static files..."
    sudo docker-compose exec web python manage.py collectstatic --noinput
    print_success "Static files collected."
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    print_status "Setting up SSL certificate..."
    
    # Stop nginx temporarily
    sudo systemctl stop nginx
    
    # Get certificate
    read -p "Enter your domain name (e.g., yourdomain.com): " DOMAIN
    sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN
    
    # Create SSL directory for nginx container
    sudo mkdir -p $PROJECT_DIR/ssl
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $PROJECT_DIR/ssl/
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $PROJECT_DIR/ssl/
    
    # Update nginx configuration
    sudo sed -i "s/your-domain.com/$DOMAIN/g" $PROJECT_DIR/nginx.conf
    
    # Restart containers
    sudo docker-compose restart nginx
    
    print_success "SSL certificate installed."
}

# Setup log rotation
setup_log_rotation() {
    print_status "Setting up log rotation..."
    
    sudo tee /etc/logrotate.d/pharmasky > /dev/null <<EOF
$LOG_FILE {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF
    
    print_success "Log rotation configured."
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up basic monitoring..."
    
    # Create health check script
    sudo tee /usr/local/bin/pharmasky-health-check > /dev/null <<'EOF'
#!/bin/bash
HEALTH_URL="http://localhost/health/"
if curl -f -s $HEALTH_URL > /dev/null; then
    echo "$(date): Service is healthy" >> /var/log/pharmasky-health.log
else
    echo "$(date): Service is down! Restarting..." >> /var/log/pharmasky-health.log
    cd /opt/pharmasky && docker-compose restart web
fi
EOF
    
    sudo chmod +x /usr/local/bin/pharmasky-health-check
    
    # Add to crontab
    (sudo crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/pharmasky-health-check") | sudo crontab -
    
    print_success "Monitoring setup complete."
}

# Main deployment function
main() {
    print_status "Starting PharmaScope deployment process..."
    
    check_prerequisites
    create_directories
    install_system_dependencies
    configure_firewall
    setup_repository
    setup_environment
    deploy_containers
    
    # Wait for containers to be ready
    print_status "Waiting for containers to be ready..."
    sleep 30
    
    run_migrations
    collect_static
    setup_log_rotation
    setup_monitoring
    
    # Optional SSL setup
    read -p "Do you want to setup SSL with Let's Encrypt? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_ssl
    fi
    
    print_success "🎉 Deployment completed successfully!"
    print_status "Your application should be available at:"
    print_status "- HTTP: http://$(curl -s ifconfig.me)"
    print_status "- Admin: http://$(curl -s ifconfig.me)/admin/"
    
    print_status "Next steps:"
    print_status "1. Update your domain DNS to point to this server"
    print_status "2. Edit /opt/pharmasky/.env.production with correct domain names"
    print_status "3. Run: cd /opt/pharmasky && sudo docker-compose restart"
    print_status "4. Create a superuser: sudo docker-compose exec web python manage.py createsuperuser"
    
    print_status "Useful commands:"
    print_status "- View logs: sudo docker-compose logs -f"
    print_status "- Restart services: sudo docker-compose restart"
    print_status "- Update deployment: sudo bash $0"
}

# Run main function
main 2>&1 | tee -a $LOG_FILE
