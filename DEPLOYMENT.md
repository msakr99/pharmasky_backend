# PharmaScope Deployment Guide for DigitalOcean

This guide will help you deploy your Django application to a DigitalOcean droplet using Docker.

## 🚀 Quick Start

1. **Create DigitalOcean Droplet**
   - Choose Ubuntu 20.04 or 22.04 LTS
   - Minimum 2GB RAM, 2 vCPUs (4GB RAM recommended for production)
   - Enable monitoring and backups

2. **Run the automated deployment script**
   ```bash
   wget -O deploy.sh https://raw.githubusercontent.com/yourusername/pharmasky/main/deploy.sh
   chmod +x deploy.sh
   sudo bash deploy.sh
   ```

## 📋 Prerequisites

### DigitalOcean Services
- [ ] Droplet (Ubuntu 20.04/22.04)
- [ ] Database (Already configured: `pharmasky-db-do-user-17921548-0.h.db.ondigitalocean.com`)
- [ ] Spaces (For media files: `pharmasky-media`)
- [ ] Domain name pointed to your droplet IP

### Required Information
- [ ] Domain name (e.g., `yourdomain.com`)
- [ ] DigitalOcean Spaces access key and secret
- [ ] Strong secret key for Django
- [ ] SSL certificate preference

## 🛠 Manual Deployment Steps

If you prefer manual deployment, follow these steps:

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional tools
sudo apt install -y git nginx certbot python3-certbot-nginx ufw
```

### 2. Firewall Configuration

```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

### 3. Clone Repository

```bash
sudo mkdir -p /opt/pharmasky
sudo chown $USER:$USER /opt/pharmasky
cd /opt/pharmasky
git clone https://github.com/yourusername/pharmasky.git .
```

### 4. Configure Environment

```bash
# Copy and edit environment file
cp production.env .env.production

# Edit with your actual values
nano .env.production
```

**Important Environment Variables:**
```env
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_DROPLET_IP
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 5. Update Nginx Configuration

```bash
# Edit nginx.conf to use your domain
sed -i 's/your-domain.com/yourdomain.com/g' nginx.conf
```

### 6. Deploy Application

```bash
# Build and start containers
docker-compose build
docker-compose up -d

# Wait for containers to start
sleep 30

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### 7. SSL Configuration (Optional but Recommended)

```bash
# Stop containers temporarily
docker-compose down

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Create SSL directory
mkdir -p ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/

# Uncomment SSL section in nginx.conf
# Then restart containers
docker-compose up -d
```

## 🔧 Management Commands

Use the management script for common tasks:

```bash
# Make script executable
chmod +x manage_deployment.sh

# Common commands
./manage_deployment.sh start          # Start services
./manage_deployment.sh stop           # Stop services
./manage_deployment.sh restart        # Restart services
./manage_deployment.sh logs           # View logs
./manage_deployment.sh status         # Check status
./manage_deployment.sh update         # Update application
./manage_deployment.sh backup         # Backup database
./manage_deployment.sh health         # Health check
./manage_deployment.sh createsuperuser # Create admin user
```

## 📊 Monitoring and Maintenance

### Application Monitoring
- Health check endpoint: `https://yourdomain.com/health/`
- Admin panel: `https://yourdomain.com/admin/`
- API documentation: `https://yourdomain.com/api/schema/swagger/`

### Log Files
- Application logs: `docker-compose logs web`
- Nginx logs: `docker-compose logs nginx`
- Celery logs: `docker-compose logs celery`

### Backup Strategy
```bash
# Automated daily backups (add to crontab)
0 2 * * * /opt/pharmasky/manage_deployment.sh backup
```

### SSL Certificate Renewal
```bash
# Add to crontab for automatic renewal
0 3 * * 1 /opt/pharmasky/manage_deployment.sh ssl
```

## 🚨 Troubleshooting

### Common Issues

1. **Containers not starting**
   ```bash
   docker-compose logs
   docker-compose ps
   ```

2. **Database connection issues**
   - Check database credentials in `.env.production`
   - Ensure database server is accessible
   - Verify SSL settings

3. **Static files not loading**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   docker-compose restart nginx
   ```

4. **Permission issues**
   ```bash
   sudo chown -R $USER:$USER /opt/pharmasky
   ```

5. **SSL certificate issues**
   ```bash
   sudo certbot renew --dry-run
   ```

### Performance Optimization

1. **Database optimization**
   - Monitor query performance
   - Use database indexing
   - Consider read replicas for high traffic

2. **Caching**
   - Redis is already configured
   - Implement Django caching framework
   - Use CDN for static files

3. **Server resources**
   - Monitor CPU and memory usage
   - Scale vertically or horizontally as needed
   - Use DigitalOcean monitoring

## 📝 Security Checklist

- [ ] Strong secret key configured
- [ ] Debug mode disabled in production
- [ ] HTTPS enabled with valid SSL certificate
- [ ] Firewall properly configured
- [ ] Database credentials secured
- [ ] Regular security updates applied
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured

## 🔗 Useful URLs

- **Application**: https://yourdomain.com
- **Admin Panel**: https://yourdomain.com/admin/
- **API Docs**: https://yourdomain.com/api/schema/swagger/
- **Health Check**: https://yourdomain.com/health/

## 📞 Support

For deployment issues:
1. Check application logs: `docker-compose logs`
2. Verify configuration files
3. Check DigitalOcean service status
4. Review this deployment guide

## 🔄 Updates

To update your deployment:
```bash
cd /opt/pharmasky
./manage_deployment.sh update
```

This will:
- Pull latest code from repository
- Rebuild Docker containers
- Run database migrations
- Collect static files
- Restart services
