# 🚀 Quick Start Guide - Docker Deployment

เริ่มต้นใช้งาน Deep Instinct to Mattermost ด้วย Docker ใน 5 นาที!

## ✅ Prerequisites

- Docker และ Docker Compose ติดตั้งแล้ว
- API credentials จาก Deep Instinct
- Mattermost Webhook URL

## 📝 Step-by-Step Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd deep-api
```

### 2. Setup Environment

```bash
# สร้างไฟล์ .env จาก template
make install

# หรือ
cp .env.docker .env
```

### 3. Edit Configuration

แก้ไข `.env` file:

```bash
nano .env
```

ระบุค่าต่อไปนี้ (ขั้นต่ำ):

```env
DEEPINSTINCT_URL=https://ro.customers.deepinstinctweb.com/api/v1/
TOKENS_KEY=your_jwt_token_here
MATTERMOST_WEBHOOK_URL=https://your-mattermost.com/hooks/xxx
```

### 4. Start Services

```bash
# Build และ Start
make up

# หรือ
docker-compose up -d
```

### 5. Verify Services

```bash
# ตรวจสอบ status
make ps

# ดู logs
make logs
```

## 🎯 Common Commands

```bash
# Start services
make up

# Stop services
make down

# View logs
make logs

# Run manual report
make report

# Run report for specific date
make report-date DATE=2026-02-13

# Open shell
make shell

# Test connection
make test

# Show help
make help
```

## 📊 Accessing Reports

- **Local**: `http://localhost:8080/event_detail/`
- **Reports saved in**: `./event_detail/`

## 🔧 Configuration Options

### Daily Report Schedule

แก้ไขใน `.env`:

```env
# รายงานเวลา 8:00 AM ทุกวัน (default)
DAILY_REPORT_CRON=0 8 * * *

# รายงาน 9 AM และ 5 PM
DAILY_REPORT_CRON=0 9,17 * * *

# รายงานจันทร์-ศุกร์ 8 AM
DAILY_REPORT_CRON=0 8 * * 1-5
```

### Monitor Polling Interval

```env
# ตรวจสอบทุก 5 นาที (default)
POLLING_INTERVAL=300

# ตรวจสอบทุก 1 นาที
POLLING_INTERVAL=60
```

### Optional: IT Parcel Integration

```env
IT_PARCEL_API_URL=https://your-itparcel.com/api/v1
IT_PARCEL_TOKEN=your_token
```

## 🏗️ Service Overview

### 3 Services Running

1. **report-server** (Port 8080)
   - HTTP server สำหรับ serve reports
   - เปิด 24/7

2. **daily-report** (Cron-based)
   - สร้างรายงานประจำวัน
   - ตามเวลาที่กำหนดใน `DAILY_REPORT_CRON`

3. **monitor** (Continuous)
   - ตรวจสอบ events แบบ real-time
   - ส่ง notification ทันที

## 🔍 Monitoring

### View Logs

```bash
# All services
make logs

# Specific service
make logs-monitor
make logs-report
make logs-daily
```

### Check Health

```bash
# Service status
docker-compose ps

# Resource usage
make stats
```

### Manual Testing

```bash
# Test API connection
make test

# Run report manually
make report

# Run report for yesterday
make report-date DATE=$(date -d yesterday +%Y-%m-%d)
```

## ⚠️ Troubleshooting

### Services not starting?

```bash
# Check logs
make logs

# Verify .env file
cat .env

# Try rebuild
make down
make build
make up
```

### Port 8080 already in use?

แก้ไขใน `.env`:

```env
REPORT_SERVER_PORT=8081
```

### Can't connect to Deep Instinct API?

```bash
# Test connection
make test

# Check credentials in .env
grep DEEPINSTINCT .env
```

## 🎓 Next Steps

- อ่านเอกสารฉบับเต็ม: [README_DOCKER.md](README_DOCKER.md)
- ตั้งค่า IT Parcel integration (optional)
- ปรับเวลารายงานตามต้องการ
- ตั้งค่า backup scripts

## 💡 Tips

1. **Backup Reports**: Reports จะถูกเก็บใน `./event_detail/`
2. **View Logs**: ใช้ `make logs` เพื่อดู real-time logs
3. **Manual Report**: ใช้ `make report` เมื่อต้องการรายงานนอกเวลา
4. **Development**: ใช้ `docker-compose.override.yml` สำหรับ dev settings

## 📞 Need Help?

1. ตรวจสอบ logs: `make logs`
2. อ่าน [README_DOCKER.md](README_DOCKER.md)
3. ลอง restart: `make restart`

---

**เริ่มต้นเลย!** 🚀

```bash
make install  # ตั้งค่า .env
# แก้ไข .env ใส่ credentials
make up       # Start!
make logs     # ดู logs
```
