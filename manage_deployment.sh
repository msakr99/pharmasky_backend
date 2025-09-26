#!/bin/bash

# PharmaScope Deployment Management Script
# This script provides common management tasks for the deployed application

set -e

PROJECT_DIR="/opt/pharmasky"
cd $PROJECT_DIR

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

show_help() {
    echo "PharmaScope Deployment Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start           Start all services"
    echo "  stop            Stop all services"
    echo "  restart         Restart all services"
    echo "  logs            Show application logs"
    echo "  status          Show container status"
    echo "  update          Update application code"
    echo "  migrate         Run database migrations"
    echo "  collectstatic   Collect static files"
    echo "  shell           Open Django shell"
    echo "  createsuperuser Create Django superuser"
    echo "  backup          Create database backup"
    echo "  restore         Restore database backup"
    echo "  health          Check application health"
    echo "  clean           Clean up unused Docker images"
    echo "  ssl             Renew SSL certificate"
    echo "  help            Show this help message"
}

start_services() {
    print_status "Starting services..."
    docker-compose up -d
    print_success "Services started successfully."
}

stop_services() {
    print_status "Stopping services..."
    docker-compose down
    print_success "Services stopped successfully."
}

restart_services() {
    print_status "Restarting services..."
    docker-compose restart
    print_success "Services restarted successfully."
}

show_logs() {
    print_status "Showing application logs..."
    docker-compose logs -f --tail=100 web
}

show_status() {
    print_status "Container status:"
    docker-compose ps
    echo ""
    print_status "Resource usage:"
    docker stats --no-stream
}

update_application() {
    print_status "Updating application..."
    
    # Pull latest code
    git pull origin main
    
    # Rebuild containers
    docker-compose build --no-cache web
    
    # Restart services
    docker-compose up -d
    
    # Run migrations
    docker-compose exec web python manage.py migrate
    
    # Collect static files
    docker-compose exec web python manage.py collectstatic --noinput
    
    print_success "Application updated successfully."
}

run_migrations() {
    print_status "Running database migrations..."
    docker-compose exec web python manage.py migrate
    print_success "Migrations completed successfully."
}

collect_static() {
    print_status "Collecting static files..."
    docker-compose exec web python manage.py collectstatic --noinput
    print_success "Static files collected successfully."
}

django_shell() {
    print_status "Opening Django shell..."
    docker-compose exec web python manage.py shell
}

create_superuser() {
    print_status "Creating Django superuser..."
    docker-compose exec web python manage.py createsuperuser
}

backup_database() {
    print_status "Creating database backup..."
    
    BACKUP_DIR="/opt/backups"
    BACKUP_FILE="pharmasky_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    mkdir -p $BACKUP_DIR
    
    # Get database credentials from environment
    DB_NAME="defaultdb"
    DB_USER="doadmin"
    DB_HOST="pharmasky-db-do-user-17921548-0.h.db.ondigitalocean.com"
    DB_PORT="25060"
    
    print_warning "You will need to enter the database password."
    pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > $BACKUP_DIR/$BACKUP_FILE
    
    print_success "Database backup created: $BACKUP_DIR/$BACKUP_FILE"
}

restore_database() {
    print_warning "This will restore the database from a backup file."
    read -p "Enter backup file path: " BACKUP_FILE
    
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    print_warning "This will overwrite the current database. Are you sure? (y/N)"
    read -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Restore cancelled."
        exit 0
    fi
    
    print_status "Restoring database..."
    
    # Database credentials
    DB_NAME="defaultdb"
    DB_USER="doadmin"
    DB_HOST="pharmasky-db-do-user-17921548-0.h.db.ondigitalocean.com"
    DB_PORT="25060"
    
    print_warning "You will need to enter the database password."
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < $BACKUP_FILE
    
    print_success "Database restored successfully."
}

health_check() {
    print_status "Checking application health..."
    
    # Check if containers are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Some containers are not running!"
        docker-compose ps
        return 1
    fi
    
    # Check HTTP endpoints
    if curl -f -s http://localhost/health/ > /dev/null; then
        print_success "HTTP health check passed."
    else
        print_error "HTTP health check failed!"
        return 1
    fi
    
    # Check database connection
    if docker-compose exec -T web python manage.py check --database default > /dev/null; then
        print_success "Database connection check passed."
    else
        print_error "Database connection check failed!"
        return 1
    fi
    
    # Check Redis connection
    if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        print_success "Redis connection check passed."
    else
        print_error "Redis connection check failed!"
        return 1
    fi
    
    print_success "All health checks passed!"
}

clean_docker() {
    print_status "Cleaning up unused Docker images..."
    docker system prune -f
    docker image prune -f
    print_success "Docker cleanup completed."
}

renew_ssl() {
    print_status "Renewing SSL certificate..."
    certbot renew --quiet
    
    # Copy renewed certificates to project directory
    if [ -d "/etc/letsencrypt/live" ]; then
        DOMAIN=$(ls /etc/letsencrypt/live | head -n 1)
        if [ -n "$DOMAIN" ]; then
            cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $PROJECT_DIR/ssl/
            cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $PROJECT_DIR/ssl/
            docker-compose restart nginx
            print_success "SSL certificate renewed and nginx restarted."
        fi
    fi
}

# Main command handler
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    update)
        update_application
        ;;
    migrate)
        run_migrations
        ;;
    collectstatic)
        collect_static
        ;;
    shell)
        django_shell
        ;;
    createsuperuser)
        create_superuser
        ;;
    backup)
        backup_database
        ;;
    restore)
        restore_database
        ;;
    health)
        health_check
        ;;
    clean)
        clean_docker
        ;;
    ssl)
        renew_ssl
        ;;
    help|*)
        show_help
        ;;
esac
