# Production Deployment Guide

คู่มือการ deploy ระบบ Deep Instinct to Mattermost แบบ production-ready

## 📋 Table of Contents

- [Deployment Options](#deployment-options)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Traditional Systemd Deployment](#traditional-systemd-deployment)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)
- [Security Best Practices](#security-best-practices)

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended)

✅ **Best for**: Single server, easy management  
✅ **Complexity**: Low  
✅ **Scalability**: Limited  

### Option 2: Kubernetes

✅ **Best for**: Multi-server, high availability  
✅ **Complexity**: High  
✅ **Scalability**: Excellent  

### Option 3: Traditional Systemd

✅ **Best for**: Legacy systems, no Docker  
✅ **Complexity**: Medium  
✅ **Scalability**: Limited  

---

## 1️⃣ Docker Compose Deployment

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Application Setup

```bash
# Clone repository
git clone <repo-url>
cd deep-api

# Create .env file
cp .env.docker .env
nano .env  # Edit with your credentials
```

### Step 3: Deploy

```bash
# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or use Makefile
make build
make up
```

### Step 4: Verify Deployment

```bash
# Check services
docker-compose ps

# View logs
docker-compose logs -f

# Test endpoint
curl http://localhost:8080/health
```

### Step 5: Setup Monitoring

```bash
# Enable Prometheus metrics (optional)
docker-compose --profile monitoring up -d

# Access Grafana at http://localhost:3000
```

---

## 2️⃣ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Helm 3+

### Step 1: Create Namespace

```bash
kubectl create namespace deep-api
```

### Step 2: Create Secrets

```bash
# Create secret from .env file
kubectl create secret generic deep-api-secrets \
  --from-env-file=.env \
  -n deep-api
```

### Step 3: Deploy with Helm (Coming Soon)

```bash
# Add Helm repository
helm repo add deep-api https://your-helm-repo.com

# Install
helm install deep-api deep-api/deep-api \
  -n deep-api \
  -f values.yaml
```

### Step 4: Expose Service

```bash
# Create ingress
kubectl apply -f k8s/ingress.yaml

# Or use LoadBalancer
kubectl expose deployment deep-api-report-server \
  --type=LoadBalancer \
  --port=80 \
  --target-port=8080 \
  -n deep-api
```

---

## 3️⃣ Traditional Systemd Deployment

### Step 1: Install Dependencies

```bash
# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv /opt/deep-api/venv
source /opt/deep-api/venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Create Systemd Services

#### Report Server Service

```bash
sudo nano /etc/systemd/system/deep-api-report-server.service
```

```ini
[Unit]
Description=Deep Instinct Report Server
After=network.target

[Service]
Type=simple
User=api
Group=api
WorkingDirectory=/opt/deep-api
Environment="PATH=/opt/deep-api/venv/bin"
EnvironmentFile=/opt/deep-api/.env
ExecStart=/opt/deep-api/venv/bin/python3 serve_reports.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Monitor Service

```bash
sudo nano /etc/systemd/system/deep-api-monitor.service
```

```ini
[Unit]
Description=Deep Instinct Monitor
After=network.target

[Service]
Type=simple
User=api
Group=api
WorkingDirectory=/opt/deep-api
Environment="PATH=/opt/deep-api/venv/bin"
EnvironmentFile=/opt/deep-api/.env
ExecStart=/opt/deep-api/venv/bin/python3 deepinstinct_to_mattermost.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 3: Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable deep-api-report-server
sudo systemctl enable deep-api-monitor

# Start services
sudo systemctl start deep-api-report-server
sudo systemctl start deep-api-monitor

# Check status
sudo systemctl status deep-api-*
```

### Step 4: Setup Cron for Daily Reports

```bash
# Edit crontab
crontab -e

# Add daily report job (8 AM daily)
0 8 * * * cd /opt/deep-api && /opt/deep-api/venv/bin/python3 send_today_to_mattermost.py >> /var/log/deep-api/daily-report.log 2>&1
```

---

## 📊 Monitoring and Logging

### Docker Compose Monitoring

#### Using Docker logs

```bash
# View logs
docker-compose logs -f

# Export logs
docker-compose logs > logs.txt
```

#### Using Prometheus + Grafana

```bash
# Start monitoring stack
docker-compose --profile monitoring up -d

# Access Grafana
open http://localhost:3000
```

### Systemd Monitoring

```bash
# View logs
journalctl -u deep-api-report-server -f
journalctl -u deep-api-monitor -f

# Check service status
systemctl status deep-api-*
```

### Log Aggregation (ELK Stack)

1. Install Filebeat
2. Configure log forwarding
3. View logs in Kibana

---

## 💾 Backup and Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/deep-api"
DATE=$(date +%Y%m%d-%H%M%S)

# Backup reports
tar -czf "$BACKUP_DIR/reports-$DATE.tar.gz" event_detail/

# Backup logs
tar -czf "$BACKUP_DIR/logs-$DATE.tar.gz" logs/

# Backup configuration
cp .env "$BACKUP_DIR/.env-$DATE"

# Keep only last 7 days
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /opt/deep-api/backup.sh
```

### Recovery

```bash
# Restore reports
tar -xzf reports-20260213.tar.gz -C /opt/deep-api/

# Restore configuration
cp .env-20260213 .env

# Restart services
docker-compose restart
```

---

## 🔒 Security Best Practices

### 1. Secure Secrets Management

```bash
# Use Docker secrets
echo "your_token" | docker secret create deep_instinct_token -

# Or use HashiCorp Vault
vault kv put secret/deep-api \
  TOKENS_KEY="your_token" \
  MATTERMOST_WEBHOOK_URL="your_webhook"
```

### 2. Network Security

```bash
# Use internal Docker network
docker network create --internal deep-api-internal

# Expose only necessary ports
# Use reverse proxy (nginx) for SSL termination
```

### 3. File Permissions

```bash
# Restrict .env file
chmod 600 .env
chown root:root .env

# Restrict report directory
chmod 755 event_detail/
chown api:api event_detail/
```

### 4. SSL/TLS Configuration

```bash
# Generate SSL certificate (Let's Encrypt)
sudo certbot certonly --standalone -d your-domain.com

# Configure nginx with SSL
# See nginx/nginx.conf for SSL configuration
```

### 5. Regular Updates

```bash
# Update Docker images
docker-compose pull
docker-compose up -d

# Update system packages
sudo apt update && sudo apt upgrade -y
```

---

## 🔍 Health Checks

### Automated Health Checks

```bash
#!/bin/bash
# health-check.sh

# Check report server
if ! curl -f http://localhost:8080 > /dev/null 2>&1; then
    echo "Report server is down!"
    # Send alert to Mattermost
fi

# Check monitor process
if ! docker-compose ps monitor | grep -q "Up"; then
    echo "Monitor is down!"
    # Send alert
fi
```

### Run health checks periodically

```bash
# Add to crontab
*/5 * * * * /opt/deep-api/health-check.sh
```

---

## 📈 Performance Tuning

### Docker Resource Limits

```yaml
# docker-compose.yml
services:
  report-server:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Python Optimization

```python
# Use connection pooling
# Enable caching for repeated API calls
# Optimize database queries (when implemented)
```

---

## 🎯 Scaling

### Horizontal Scaling (Multiple Instances)

```bash
# Scale monitor instances
docker-compose up -d --scale monitor=3

# Use load balancer for report-server
docker-compose up -d --scale report-server=2
```

### Load Balancing with Nginx

See `nginx/nginx.conf` for load balancing configuration.

---

## 📞 Support and Troubleshooting

### Common Issues

1. **Services not starting**
   - Check logs: `docker-compose logs`
   - Verify .env configuration
   - Check port conflicts

2. **API connection failures**
   - Test with: `make test`
   - Verify credentials
   - Check network connectivity

3. **Performance issues**
   - Monitor resources: `docker stats`
   - Check disk space
   - Review logs for errors

### Get Help

- Check documentation: [README_DOCKER.md](README_DOCKER.md)
- View logs: `make logs`
- Open issue on GitHub

---

**Ready for Production!** 🚀
