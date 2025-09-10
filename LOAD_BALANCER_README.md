# CampusHub360 Load Balancer Setup

This document provides comprehensive instructions for deploying CampusHub360 with a high-performance load balancer setup on AWS EC2.

## 🏗️ Architecture Overview

The load balancer setup includes:
- **Nginx Load Balancer**: Distributes traffic across multiple Django instances
- **4 Django Application Instances**: Horizontally scaled web servers
- **Redis Cache**: Shared caching layer
- **Health Monitoring**: Automated health checks and scaling
- **SSL/TLS Support**: HTTPS encryption with Let's Encrypt
- **Monitoring & Metrics**: Performance monitoring and alerting

## 📁 Files Created

### Core Configuration Files
- `docker-compose.loadbalancer.yml` - Load balancer Docker Compose configuration
- `nginx/nginx-lb.conf` - Enhanced Nginx configuration with load balancing
- `nginx/nginx-lb-https.conf` - HTTPS-enabled Nginx configuration

### Deployment Scripts
- `deploy-loadbalancer.sh` - Complete load balancer deployment script
- `manage-loadbalancer.sh` - Management script for load balancer operations
- `monitor-and-scale.sh` - Health monitoring and auto-scaling script
- `setup-ssl.sh` - SSL/TLS certificate setup script

## 🚀 Quick Start

### 1. Deploy Load Balancer
```bash
# Make scripts executable
chmod +x *.sh

# Deploy the load balancer
./deploy-loadbalancer.sh
```

### 2. Manage Load Balancer
```bash
# Check status
./manage-loadbalancer.sh status

# Scale instances
./manage-loadbalancer.sh scale 6

# View logs
./manage-loadbalancer.sh logs nginx-lb

# Start monitoring
./manage-loadbalancer.sh monitor
```

### 3. Setup SSL (Optional)
```bash
# For testing (self-signed certificate)
./setup-ssl.sh self-signed

# For production (Let's Encrypt)
./setup-ssl.sh letsencrypt campushub360.xyz admin@example.com
```

## 🔧 Configuration Details

### Load Balancing Algorithm
- **Method**: `least_conn` - Routes requests to the server with the least active connections
- **Health Checks**: Automatic failover for unhealthy instances
- **Connection Pooling**: Keep-alive connections for better performance

### Rate Limiting
- **API Endpoints**: 100 requests/second per IP
- **Authentication**: 10 requests/second per IP
- **Static Files**: 200 requests/second per IP
- **Connection Limit**: 20 concurrent connections per IP

### Caching Strategy
- **Static Files**: 1 year cache with immutable headers
- **API Responses**: 5 minutes cache for GET requests
- **Media Files**: 1 year cache
- **Admin Interface**: No caching

### Security Features
- **Security Headers**: HSTS, XSS Protection, Content Security Policy
- **SSL/TLS**: TLS 1.2/1.3 with strong cipher suites
- **Rate Limiting**: Protection against DDoS attacks
- **Connection Limits**: Prevention of connection exhaustion

## 📊 Monitoring & Scaling

### Auto-Scaling Configuration
- **Min Instances**: 2
- **Max Instances**: 8
- **Scale Up Threshold**: 80% CPU/Memory usage
- **Scale Down Threshold**: 30% CPU/Memory usage
- **Check Interval**: 30 seconds

### Health Monitoring
- **Health Check Endpoint**: `/health/`
- **Check Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3 attempts

### Metrics Available
- **Nginx Metrics**: Available at `:9113/metrics`
- **Redis Commander**: Available at `:8081`
- **Container Stats**: CPU, Memory, Network, Disk usage

## 🛠️ Management Commands

### Basic Operations
```bash
# Start load balancer
./manage-loadbalancer.sh start

# Stop load balancer
./manage-loadbalancer.sh stop

# Restart load balancer
./manage-loadbalancer.sh restart

# Check status
./manage-loadbalancer.sh status
```

### Scaling Operations
```bash
# Scale to 6 instances
./manage-loadbalancer.sh scale 6

# Check current scaling
docker compose -f docker-compose.loadbalancer.yml ps
```

### Monitoring Operations
```bash
# View logs
./manage-loadbalancer.sh logs
./manage-loadbalancer.sh logs nginx-lb

# Check health
./manage-loadbalancer.sh health

# View statistics
./manage-loadbalancer.sh stats
```

### Maintenance Operations
```bash
# Backup configuration and data
./manage-loadbalancer.sh backup

# Restore from backup
./manage-loadbalancer.sh restore backups/20241211_120000

# Update services
./manage-loadbalancer.sh update
```

## 🔒 SSL/TLS Setup

### Self-Signed Certificate (Testing)
```bash
./setup-ssl.sh self-signed
```

### Let's Encrypt Certificate (Production)
```bash
./setup-ssl.sh letsencrypt campushub360.xyz admin@example.com
```

### Manual Certificate Setup
1. Place your certificate files in `nginx/ssl/`:
   - `cert.pem` - Certificate file
   - `key.pem` - Private key file
2. Update `docker-compose.loadbalancer.yml` to use `nginx-lb-https.conf`
3. Restart the load balancer

## 📈 Performance Optimization

### Nginx Optimizations
- **Gzip Compression**: Enabled for text-based content
- **Connection Pooling**: Keep-alive connections
- **Buffer Optimization**: Optimized proxy buffers
- **Static File Caching**: Long-term caching for static assets

### Django Optimizations
- **Gunicorn Workers**: 4 workers per instance
- **Worker Class**: Sync workers for stability
- **Connection Pooling**: 1000 connections per worker
- **Preload Application**: Faster startup times

### Redis Optimizations
- **Memory Limit**: 1GB with LRU eviction
- **Persistence**: AOF (Append Only File) enabled
- **Connection Pooling**: Shared connections across instances

## 🚨 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check for port usage
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Kill processes using ports
sudo fuser -k 80/tcp
sudo fuser -k 443/tcp
```

#### Health Check Failures
```bash
# Check individual service health
docker compose -f docker-compose.loadbalancer.yml ps
docker compose -f docker-compose.loadbalancer.yml logs web1

# Test health endpoint manually
curl -v http://localhost/health/
```

#### High Resource Usage
```bash
# Check resource usage
docker stats

# Scale up instances
./manage-loadbalancer.sh scale 8

# Start monitoring
./manage-loadbalancer.sh monitor
```

#### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Renew Let's Encrypt certificate
sudo certbot renew --dry-run
```

### Log Locations
- **Nginx Logs**: `docker compose -f docker-compose.loadbalancer.yml logs nginx-lb`
- **Django Logs**: `docker compose -f docker-compose.loadbalancer.yml logs web1`
- **Redis Logs**: `docker compose -f docker-compose.loadbalancer.yml logs redis`

## 🔄 Backup & Recovery

### Automated Backup
```bash
# Create backup
./manage-loadbalancer.sh backup

# Backup includes:
# - Configuration files
# - Nginx configuration
# - SSL certificates
# - Redis data
# - Management scripts
```

### Manual Backup
```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d_%H%M%S)

# Backup configuration
cp docker-compose.loadbalancer.yml backups/$(date +%Y%m%d_%H%M%S)/
cp -r nginx/ backups/$(date +%Y%m%d_%H%M%S)/

# Backup Redis data
docker run --rm -v campushub360_redis_data:/data -v $(pwd)/backups/$(date +%Y%m%d_%H%M%S):/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
```

## 📋 Production Checklist

### Before Deployment
- [ ] Update domain names in configuration files
- [ ] Set up proper DNS records
- [ ] Configure firewall rules (ports 80, 443)
- [ ] Set up SSL certificates
- [ ] Configure monitoring and alerting
- [ ] Set up log aggregation
- [ ] Configure backup strategy

### After Deployment
- [ ] Test all endpoints
- [ ] Verify SSL certificate
- [ ] Check health monitoring
- [ ] Test auto-scaling
- [ ] Verify backup process
- [ ] Set up monitoring alerts
- [ ] Document access credentials

## 🌐 Access URLs

### Production URLs
- **Main Application**: `https://campushub360.xyz`
- **Admin Panel**: `https://campushub360.xyz/admin/`
- **Health Check**: `https://campushub360.xyz/health/`
- **API Endpoints**: `https://campushub360.xyz/api/`

### Monitoring URLs
- **Redis Commander**: `http://13.232.220.214:8081`
- **Nginx Metrics**: `http://13.232.220.214:9113/metrics`

### Default Credentials
- **Admin Username**: `admin`
- **Admin Password**: `Admin@123`
- **Admin Email**: `admin@example.com`

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs using `./manage-loadbalancer.sh logs`
3. Check health status using `./manage-loadbalancer.sh health`
4. Verify configuration files
5. Check resource usage with `./manage-loadbalancer.sh stats`

---

**Note**: This load balancer setup is designed for production use with high availability and performance. Make sure to customize the configuration according to your specific requirements and security policies.
