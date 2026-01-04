#!/bin/bash
# Initial deployment script for fresh server setup
# For code updates, use: ./redeploy.sh
set -e

SERVER="root@49.13.204.222"
DOMAIN="show-your.app"
APP_DIR="/opt/vibe_hub"

echo "=== Vibe Hub Initial Deployment ==="
echo "Server: $SERVER | Domain: $DOMAIN"
echo ""

[[ ! -f ".env.production" ]] && echo "Error: .env.production not found!" && exit 1

# Install Docker
echo "Installing Docker..."
ssh $SERVER << 'EOF'
if ! command -v docker &> /dev/null; then
    apt-get update && apt-get install -y ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl enable docker && systemctl start docker
fi
docker --version && docker compose version
EOF

# Copy files
echo "Copying files..."
ssh $SERVER "mkdir -p $APP_DIR"
rsync -az --delete \
    --exclude 'node_modules' --exclude '.venv' --exclude '__pycache__' \
    --exclude '.git' --exclude '*.pyc' --exclude '.env' \
    --exclude 'vibe_hub.db' --exclude '.pytest_cache' --exclude 'dist' \
    ./ $SERVER:$APP_DIR/
scp .env.production $SERVER:$APP_DIR/.env

# Setup SSL
echo "Setting up SSL..."
ssh $SERVER "cd $APP_DIR && mkdir -p nginx"

# Create temp nginx config locally and copy
cat > /tmp/nginx-initial.conf << CONF
server {
    listen 80;
    server_name $DOMAIN;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 200 'Setting up...'; add_header Content-Type text/plain; }
}
CONF
scp /tmp/nginx-initial.conf $SERVER:$APP_DIR/nginx/nginx-initial.conf

ssh $SERVER << EOF
docker stop temp-nginx 2>/dev/null || true
docker rm temp-nginx 2>/dev/null || true
docker run -d --name temp-nginx -p 80:80 \
    -v $APP_DIR/nginx/nginx-initial.conf:/etc/nginx/conf.d/default.conf:ro \
    -v certbot_webroot:/var/www/certbot nginx:alpine
sleep 3

docker run --rm -v certbot_webroot:/var/www/certbot -v certbot_certs:/etc/letsencrypt \
    certbot/certbot certonly --webroot --webroot-path=/var/www/certbot \
    --email admin@$DOMAIN --agree-tos --no-eff-email -d $DOMAIN

docker stop temp-nginx && docker rm temp-nginx

# Copy certs to compose volume
docker run --rm -v certbot_certs:/src:ro -v vibe_hub_certbot_certs:/dst alpine sh -c "cp -r /src/* /dst/"
EOF

# Start services
echo "Starting services..."
ssh $SERVER << EOF
cd $APP_DIR
docker compose -f docker-compose.prod.yml up -d --build
sleep 10
docker compose -f docker-compose.prod.yml ps
EOF

# Setup SSL renewal cron
ssh $SERVER << 'EOF'
(crontab -l 2>/dev/null | grep -v certbot; echo "0 0,12 * * * cd /opt/vibe_hub && docker compose -f docker-compose.prod.yml exec -T certbot certbot renew --quiet") | crontab -
EOF

echo ""
echo "=== Deployment complete! ==="
echo "App: https://$DOMAIN"
echo "For updates: ./redeploy.sh"
