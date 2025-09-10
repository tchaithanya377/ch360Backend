#!/bin/bash

# CampusHub360 SSL/TLS Setup Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

print_header "=== CampusHub360 SSL/TLS Setup ==="

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    print_status "Installing certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
fi

# Create SSL directory
mkdir -p nginx/ssl

# Function to generate self-signed certificate (for testing)
generate_self_signed() {
    print_status "Generating self-signed certificate for testing..."
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=campushub360.xyz"
    
    print_warning "Self-signed certificate generated. This should only be used for testing!"
    print_warning "For production, use Let's Encrypt or a trusted CA certificate."
}

# Function to setup Let's Encrypt certificate
setup_letsencrypt() {
    local domain=$1
    local email=$2
    
    if [ -z "$domain" ] || [ -z "$email" ]; then
        print_error "Domain and email are required for Let's Encrypt setup"
        print_error "Usage: $0 letsencrypt <domain> <email>"
        exit 1
    fi
    
    print_status "Setting up Let's Encrypt certificate for $domain..."
    
    # Stop nginx temporarily
    docker compose -f docker-compose.loadbalancer.yml stop nginx-lb || true
    
    # Generate certificate
    sudo certbot certonly --standalone -d $domain -d www.$domain --email $email --agree-tos --non-interactive
    
    # Copy certificates to nginx directory
    sudo cp /etc/letsencrypt/live/$domain/fullchain.pem nginx/ssl/cert.pem
    sudo cp /etc/letsencrypt/live/$domain/privkey.pem nginx/ssl/key.pem
    sudo chown $USER:$USER nginx/ssl/*.pem
    
    print_status "Let's Encrypt certificate installed successfully!"
    
    # Setup auto-renewal
    print_status "Setting up certificate auto-renewal..."
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'docker compose -f $(pwd)/docker-compose.loadbalancer.yml restart nginx-lb'") | crontab -
    
    print_status "Certificate auto-renewal configured!"
}

# Function to update nginx configuration for HTTPS
update_nginx_https() {
    print_status "Updating nginx configuration for HTTPS..."
    
    # Create HTTPS-enabled nginx config
    cat > nginx/nginx-lb-https.conf << 'EOF'
# Enhanced Nginx Load Balancer Configuration with HTTPS
upstream django_backend {
    least_conn;
    server web1:8000 weight=3 max_fails=3 fail_timeout=30s;
    server web2:8000 weight=3 max_fails=3 fail_timeout=30s;
    server web3:8000 weight=3 max_fails=3 fail_timeout=30s;
    server web4:8000 weight=3 max_fails=3 fail_timeout=30s;
    keepalive 32;
    keepalive_requests 100;
    keepalive_timeout 60s;
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name campushub360.xyz www.campushub360.xyz;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name campushub360.xyz www.campushub360.xyz;
    
    # SSL configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self';" always;
    
    # Connection limits
    limit_conn conn_limit_per_ip 20;
    
    # Client settings
    client_max_body_size 10M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/atom+xml image/svg+xml;

    # Static files
    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    location /media/ {
        alias /app/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Health check
    location /health/ {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        access_log off;
    }

    # API endpoints
    location /api/ {
        limit_req zone=api burst=200 nodelay;
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 5s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # All other requests
    location / {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 5s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
EOF

    print_status "HTTPS nginx configuration created!"
}

# Main script logic
case "${1:-}" in
    "self-signed")
        generate_self_signed
        update_nginx_https
        print_status "Self-signed certificate setup complete!"
        print_warning "Remember to update docker-compose.loadbalancer.yml to use nginx-lb-https.conf"
        ;;
    "letsencrypt")
        setup_letsencrypt "$2" "$3"
        update_nginx_https
        print_status "Let's Encrypt certificate setup complete!"
        print_warning "Remember to update docker-compose.loadbalancer.yml to use nginx-lb-https.conf"
        ;;
    *)
        print_error "Usage: $0 {self-signed|letsencrypt <domain> <email>}"
        print_error ""
        print_error "Examples:"
        print_error "  $0 self-signed                    # Generate self-signed certificate for testing"
        print_error "  $0 letsencrypt example.com admin@example.com  # Setup Let's Encrypt certificate"
        exit 1
        ;;
esac

print_header "SSL/TLS Setup Complete!"
print_status "Next steps:"
print_status "1. Update docker-compose.loadbalancer.yml to use the HTTPS nginx config"
print_status "2. Restart the load balancer: docker compose -f docker-compose.loadbalancer.yml restart nginx-lb"
print_status "3. Test HTTPS access: https://your-domain.com"
