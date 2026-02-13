# 🐳 Docker Commands Cheat Sheet

คำสั่ง Docker ที่ใช้บ่อยสำหรับ Deep Instinct to Mattermost

## 🚀 Quick Start

```bash
# ติดตั้งครั้งแรก
make install        # สร้าง .env file
# แก้ไข .env ใส่ credentials
make up             # Start services
make logs           # ดู logs
```

## 📦 Service Management

```bash
# Start/Stop/Restart
make up             # Start all services
make down           # Stop all services  
make restart        # Restart all services

# Specific service
docker-compose restart report-server
docker-compose restart monitor
docker-compose restart daily-report
```

## 📊 Monitoring

```bash
# Service status
make ps
docker-compose ps

# Logs
make logs                   # All services
make logs-monitor          # Monitor only
make logs-report           # Report server only
make logs-daily            # Daily report only

# Follow logs
docker-compose logs -f
docker-compose logs -f monitor

# Last N lines
docker-compose logs --tail=50

# Resource usage
make stats
docker stats
```

## 🔧 Operations

```bash
# Run daily report manually
make report

# Run report for specific date
make report-date DATE=2026-02-13

# Test API connection
make test

# Open shell
make shell              # Monitor container
make shell-report       # Report server container

# Run command in container
docker-compose exec monitor python3 test_connection.py
docker-compose run --rm monitor python3 send_today_to_mattermost.py
```

## 🏗️ Build & Deploy

```bash
# Build images
make build
docker-compose build

# Build without cache
docker-compose build --no-cache

# Pull latest images
docker-compose pull

# Start specific service
docker-compose up -d report-server
docker-compose up -d monitor
```

## 🔍 Debugging

```bash
# Check service health
make health
docker inspect deep-api-report-server

# View container details
docker inspect deep-api-monitor

# Check logs for errors
docker-compose logs | grep -i error

# Interactive shell
docker-compose exec monitor /bin/bash
docker-compose run --rm monitor /bin/bash

# Check environment variables
docker-compose run --rm monitor env
```

## 🧹 Cleanup

```bash
# Stop and remove containers
make down
docker-compose down

# Remove with volumes
docker-compose down -v

# Full cleanup
make clean              # Remove containers & volumes
make clean-all          # Remove everything including images

# Remove unused resources
docker system prune -a
```

## 💾 Backup & Restore

```bash
# Backup
make backup

# Manual backup
tar -czf backup.tar.gz event_detail/ logs/

# Restore
tar -xzf backup.tar.gz -C /path/to/deep-api/
```

## 🔐 Configuration

```bash
# Edit environment
nano .env

# Reload configuration (restart needed)
make down
make up

# View current config
docker-compose config

# Validate config
docker-compose config --quiet
```

## 📈 Production

```bash
# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# With nginx
docker-compose --profile with-nginx up -d

# Scale services
docker-compose up -d --scale monitor=3
```

## 🎯 Development

```bash
# Development mode
make dev-up
make dev-logs

# Mount code for live reload
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Run tests
docker-compose run --rm monitor pytest
```

## 🚨 Emergency Commands

```bash
# Force restart everything
docker-compose down
docker-compose up -d --force-recreate

# View real-time resource usage
docker stats

# Kill all containers
docker kill $(docker ps -q)

# Remove all stopped containers
docker container prune -f
```

## 📝 Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Deep API shortcuts
alias dapi='cd /path/to/deep-api'
alias dapi-up='make up'
alias dapi-down='make down'
alias dapi-logs='make logs'
alias dapi-report='make report'
alias dapi-shell='make shell'
alias dapi-restart='make restart'
```

## 🔗 URLs

```bash
# Report server
http://localhost:8080

# Reports directory
http://localhost:8080/event_detail/

# Health check
curl http://localhost:8080/health

# Nginx (if enabled)
http://localhost:80
```

## 📊 Common Workflows

### Daily Operations

```bash
# Morning routine
make ps              # Check status
make logs --tail=50  # Check recent logs
make report          # Generate manual report (if needed)
```

### Troubleshooting

```bash
# Something not working?
make logs | grep -i error    # Find errors
make ps                      # Check status
make health                  # Check health
docker-compose restart       # Try restart
```

### Deployment

```bash
# Deploy new version
git pull
make build
make down
make up
make logs
```

### Maintenance

```bash
# Weekly maintenance
make backup          # Backup data
docker system prune  # Clean up unused resources
make ps              # Verify running
```

## 🆘 Help

```bash
# Show available commands
make help

# Docker Compose help
docker-compose --help

# Service logs help
docker-compose logs --help
```

## 📚 References

- Main Docs: [README.md](README.md)
- Docker Docs: [README_DOCKER.md](README_DOCKER.md)
- Quick Start: [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md)
- Deployment: [DEPLOYMENT.md](DEPLOYMENT.md)

---

**💡 Tip**: Use `make help` to see all available commands!
