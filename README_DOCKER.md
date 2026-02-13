# Deep Instinct to Mattermost - Docker Deployment

เอกสารคู่มือการ deploy ด้วย Docker Compose สำหรับระบบ Deep Instinct Integration

## 📋 Table of Contents

- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Usage](#usage)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## 🚀 Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- ไฟล์ `.env` ที่ตั้งค่าเรียบร้อย

## ⚡ Quick Start

### 1. Clone และเตรียม Environment

```bash
# Clone repository
git clone <your-repo-url>
cd deep-api

# สร้างไฟล์ .env จาก template
cp .env.docker .env

# แก้ไข .env ตามความต้องการ
nano .env
```

### 2. ตั้งค่า Environment Variables

แก้ไขไฟล์ `.env` โดยระบุค่าต่อไปนี้:

```bash
# Deep Instinct API
DEEPINSTINCT_URL=https://ro.customers.deepinstinctweb.com/api/v1/
TOKENS_KEY=your_jwt_token_here

# Mattermost Webhook
MATTERMOST_WEBHOOK_URL=https://your-mattermost.com/hooks/xxx

# Report Server (ใช้ service name ใน Docker network)
REPORT_SERVER_URL=http://report-server:8080

# Optional: IT Parcel/Snip IT
IT_PARCEL_API_URL=https://your-itparcel.com/api/v1
IT_PARCEL_TOKEN=your_token

# Cron Schedule (เวลารายงาน)
DAILY_REPORT_CRON=0 8 * * *
```

### 3. Build และ Run

```bash
# Build Docker images
docker-compose build

# Start services
docker-compose up -d

# ดู logs
docker-compose logs -f
```

## 🏗️ Architecture

Docker Compose stack ประกอบด้วย 3 services:

```
┌─────────────────────────────────────────────┐
│          Docker Network (deep-api)          │
│                                             │
│  ┌─────────────────┐  ┌─────────────────┐  │
│  │  report-server  │  │  daily-report   │  │
│  │   Port: 8080    │  │  (cron-based)   │  │
│  │  HTTP Server    │  │                 │  │
│  └────────┬────────┘  └────────┬────────┘  │
│           │                    │            │
│           └─────────┬──────────┘            │
│                     │                       │
│              ┌──────┴────────┐              │
│              │    monitor    │              │
│              │ (continuous)  │              │
│              └───────────────┘              │
│                                             │
└─────────────────────────────────────────────┘
         │                     │
         ↓                     ↓
   Deep Instinct           Mattermost
      API                   Webhook
```

### Services

#### 1. **report-server**
- รัน HTTP server บน port 8080
- Serve HTML reports สำหรับ Mattermost links
- Expose port ไปยัง host
- Auto-restart on failure

#### 2. **daily-report**
- รันรายงานประจำวันตาม cron schedule
- Default: 8:00 AM ทุกวัน (configurable)
- เก็บ logs ใน `/app/logs/daily-report.log`
- Auto-restart on failure

#### 3. **monitor**
- ตรวจสอบ events แบบ real-time
- Polling interval: 300 วินาที (5 นาที)
- ส่ง notification ไปยัง Mattermost ทันที
- Auto-restart on failure

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEEPINSTINCT_URL` | Deep Instinct API URL | - | ✅ |
| `TOKENS_KEY` | JWT Token | - | ✅ |
| `MATTERMOST_WEBHOOK_URL` | Mattermost Webhook URL | - | ✅ |
| `REPORT_SERVER_URL` | Report Server URL | `http://report-server:8080` | ✅ |
| `REPORT_SERVER_PORT` | Report Server Port | `8080` | ❌ |
| `IT_PARCEL_API_URL` | IT Parcel/Snip IT API | - | ❌ |
| `IT_PARCEL_TOKEN` | IT Parcel Token | - | ❌ |
| `POLLING_INTERVAL` | Monitor polling interval (seconds) | `300` | ❌ |
| `DAILY_REPORT_CRON` | Cron schedule for daily report | `0 8 * * *` | ❌ |
| `TZ` | Timezone | `Asia/Bangkok` | ❌ |

### Cron Schedule Format

```
* * * * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, Sunday=0 or 7)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

ตัวอย่าง:
- `0 8 * * *` = 8:00 AM ทุกวัน
- `0 9,17 * * *` = 9:00 AM และ 5:00 PM ทุกวัน
- `0 8 * * 1-5` = 8:00 AM จันทร์-ศุกร์

## 📖 Usage

### Basic Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart report-server

# View logs
docker-compose logs -f [service-name]

# View logs for specific service
docker-compose logs -f daily-report
docker-compose logs -f monitor

# Check service status
docker-compose ps

# Rebuild services after code changes
docker-compose build
docker-compose up -d
```

### Running Manual Reports

```bash
# รัน daily report ด้วยมือ (วันนี้)
docker-compose run --rm daily-report once

# รัน report ย้อนหลัง (ระบุวันที่)
docker-compose run --rm daily-report once 2026-02-13

# รัน report วันที่แบบไทย (วัน-เดือน-ปี พ.ศ.)
docker-compose run --rm daily-report once 13-2-69
```

### Accessing Reports

Reports จะถูกเก็บไว้ที่:
- **Local**: `./event_detail/event_details_YYYY-MM-DD.html`
- **HTTP**: `http://localhost:8080/event_detail/event_details_YYYY-MM-DD.html`
- **Docker Network**: `http://report-server:8080/event_detail/event_details_YYYY-MM-DD.html`

## 📊 Monitoring

### Health Checks

Services มี health checks แบบอัตโนมัติ:

```bash
# ดู health status
docker-compose ps

# ดู health check logs
docker inspect --format='{{json .State.Health}}' deep-api-report-server | jq
```

### Logs

```bash
# Tail all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f monitor

# Last 100 lines
docker-compose logs --tail=100

# Since timestamp
docker-compose logs --since 2026-02-13T08:00:00
```

### Performance Metrics

```bash
# Resource usage
docker stats

# Specific container
docker stats deep-api-report-server
```

## 🔧 Troubleshooting

### Service ไม่ start

```bash
# ตรวจสอบ logs
docker-compose logs [service-name]

# ตรวจสอบ configuration
docker-compose config

# ลองรัน interactive mode
docker-compose run --rm monitor /bin/bash
```

### Environment variables ไม่ถูกโหลด

```bash
# ตรวจสอบว่าไฟล์ .env มีอยู่
ls -la .env

# ตรวจสอบค่าที่โหลดใน container
docker-compose run --rm monitor env | grep DEEPINSTINCT
```

### Port ถูกใช้งานแล้ว

ถ้า port 8080 ถูกใช้งาน แก้ไขใน `.env`:

```bash
REPORT_SERVER_PORT=8081
```

แล้ว restart:

```bash
docker-compose down
docker-compose up -d
```

### Permission issues กับ volumes

```bash
# Fix permissions
sudo chown -R $USER:$USER ./event_detail ./logs

# หรือเปลี่ยน permissions
chmod -R 755 ./event_detail ./logs
```

## 🛠️ Development

### Development Mode

สร้างไฟล์ `docker-compose.override.yml` สำหรับ development:

```yaml
version: '3.8'

services:
  report-server:
    volumes:
      - .:/app:rw  # Mount source code for live reload
    environment:
      - DEBUG=1
  
  monitor:
    volumes:
      - .:/app:rw
    environment:
      - DEBUG=1
      - POLLING_INTERVAL=60  # Faster polling for testing
```

### Testing

```bash
# Test API connection
docker-compose run --rm monitor python3 test_connection.py

# Run single report
docker-compose run --rm daily-report once

# Interactive shell
docker-compose run --rm monitor /bin/bash
```

### Building

```bash
# Build without cache
docker-compose build --no-cache

# Build specific service
docker-compose build report-server

# Pull latest base images
docker-compose pull
```

## 📦 Production Deployment

### Best Practices

1. **Security**
   ```bash
   # ใช้ secrets แทน .env file
   docker secret create deep_instinct_token token.txt
   ```

2. **Backup**
   ```bash
   # Backup event_detail directory
   tar -czf backup-$(date +%Y%m%d).tar.gz event_detail/
   ```

3. **Monitoring**
   - ใช้ Prometheus + Grafana
   - ตั้ง alerts สำหรับ service failures

4. **Logging**
   - ใช้ logging driver เช่น syslog, fluentd
   - Centralized logging ด้วย ELK stack

### Scaling

```bash
# Scale monitor instances
docker-compose up -d --scale monitor=3

# Use Docker Swarm for production
docker stack deploy -c docker-compose.yml deep-api
```

## 📝 Maintenance

### Cleanup

```bash
# Remove stopped containers
docker-compose down

# Remove volumes too
docker-compose down -v

# Clean up system
docker system prune -a
```

### Updates

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose build
docker-compose down
docker-compose up -d
```

## 🆘 Support

หากพบปัญหา:

1. ตรวจสอบ logs: `docker-compose logs -f`
2. ตรวจสอบ health status: `docker-compose ps`
3. ลอง restart: `docker-compose restart`
4. ถ้ายังไม่ได้ ลบแล้วสร้างใหม่: `docker-compose down && docker-compose up -d`

## 📄 License

[Your License Here]

## 👥 Authors

[Your Team/Name Here]
