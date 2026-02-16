# 🚀 Docker Production Guide - Deep API

**เอกสารฉบับสมบูรณ์สำหรับการใช้งาน Deep API บน Docker Production**

---

## 📋 สารบัญ

1. [ภาพรวมระบบ](#ภาพรวมระบบ)
2. [การติดตั้ง](#การติดตั้ง)
3. [การจัดการ Services](#การจัดการ-services)
4. [การทดสอบ](#การทดสอบ)
5. [การใช้งาน Production](#การใช้งาน-production)
6. [Database Management](#database-management)
7. [Troubleshooting](#troubleshooting)

---

## ภาพรวมระบบ

### Services ที่รันบน Docker

```
┌─────────────────────────────────────────────┐
│           Docker Compose Services          │
├─────────────────────────────────────────────┤
│                                             │
│  📡 report-server                           │
│     - HTTP Server (port 8080)               │
│     - Serve HTML reports                    │
│     - Healthcheck: http://localhost:8080    │
│                                             │
│  📅 daily-report                            │
│     - Cron scheduler                        │
│     - Daily report at 08:00 (default)       │
│     - Configurable via DAILY_REPORT_CRON    │
│                                             │
│  🔍 monitor                                 │
│     - Real-time event monitor               │
│     - Send alerts to Mattermost             │
│     - Healthcheck: process monitoring       │
│                                             │
└─────────────────────────────────────────────┘
```

### Test Scripts ใน Container

- ✅ `test_report_format.py` - ทดสอบรูปแบบ (ตัวอย่าง)
- ✅ `test_report_preview.py` - ดึงข้อมูลจริง (ไม่สร้าง HTML)
- ✅ `test_complete_report.py` - ทดสอบครบถ้วน (สร้าง HTML)
- ✅ `send_today_to_mattermost.py` - ส่งจริงไป Mattermost
- ✅ `query_events.py` - Query database
- ✅ `db_maintenance.py` - Database maintenance

---

## การติดตั้ง

### Prerequisites

```bash
# ตรวจสอบ Docker
docker --version
docker-compose --version

# ตรวจสอบไฟล์ .env
ls -la /home/api/deep-api/.env
```

### Configuration

แก้ไขไฟล์ `.env`:

```bash
# API Configuration
DEEPINSTINCT_URL=https://ro.customers.deepinstinctweb.com/api/v1/
TOKENS_KEY=your_token_here
MATTERMOST_WEBHOOK_URL=your_webhook_url_here

# IT Parcel / Snip IT Configuration
IT_PARCEL_API_URL=https://itparcel.example.com/api/v1
IT_PARCEL_TOKEN=your_snipit_token_here

# Report Server
REPORT_SERVER_PORT=8080
REPORT_SERVER_URL=https://allevent.ifn-dtc.online

# Daily Report Schedule (Cron format)
DAILY_REPORT_CRON=0 8 * * *  # ทุกวัน 08:00 น.
```

---

## การจัดการ Services

### Management Script

ใช้สคริปต์ `docker-manage.sh` สำหรับจัดการทุกอย่าง:

```bash
cd /home/api/deep-api
./docker-manage.sh [command] [options]
```

### คำสั่งพื้นฐาน

#### 1. Start Services

```bash
./docker-manage.sh start
```

**Output:**
```
╔══════════════════════════════════════════╗
║   Deep API - Production Management      ║
╚══════════════════════════════════════════╝

ℹ️  Starting Docker services...
✅ Services started!

NAME                     STATUS                  PORTS
deep-api-report-server   Up (healthy)            0.0.0.0:8080->8080/tcp
deep-api-daily-report    Up (health: starting)   
deep-api-monitor         Up (health: starting)   
```

#### 2. Stop Services

```bash
./docker-manage.sh stop
```

#### 3. Restart Services

```bash
./docker-manage.sh restart
```

#### 4. Check Status

```bash
./docker-manage.sh status
```

#### 5. View Logs

```bash
# ดู logs ทั้งหมด
./docker-manage.sh logs

# ดู logs service เดียว
./docker-manage.sh logs report-server
./docker-manage.sh logs daily-report
./docker-manage.sh logs monitor

# กด Ctrl+C เพื่อออก
```

#### 6. Rebuild Services

```bash
# Rebuild ทั้งหมดใหม่ (เมื่อมีการแก้ไข code)
./docker-manage.sh rebuild
```

---

## การทดสอบ

### 🧪 Test Commands

ทดสอบ **ก่อนส่งจริง** ไปยัง Mattermost

#### 1. Test Format (ตัวอย่างข้อมูล)

```bash
./docker-manage.sh test format
```

**จุดประสงค์:** ดูรูปแบบ message ด้วยข้อมูลตัวอย่าง

---

#### 2. Test Preview (ข้อมูลจริง, ไม่สร้าง HTML)

```bash
# เมื่อวาน
./docker-manage.sh test preview yesterday

# วันที่กำหนด (พ.ศ.)
./docker-manage.sh test preview 15-2-69

# วันที่กำหนด (ค.ศ.)
./docker-manage.sh test preview 2026-02-15
```

**จุดประสงค์:** ดึงข้อมูลจริงจาก API และแสดง preview message

**Output:**
```
📅 Report Date: 2026-02-15
📥 Fetching Malicious Events... ✅ Found 0
📥 Fetching Suspicious Events... ✅ Found 10

📨 PREVIEW MESSAGE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 Deep Instinct Security Report
วันที่: 15/02/2569 | เวลา: 11:44:47 (GMT+7)

📊 สรุป Events วันที่ 15/2/2569
┌────────────┬────────┐
│ 🔴 Malicious │ 0    │
│ 🟡 Suspicious│ 10   │
│ รวมทั้งหมด │ 10   │
└────────────┴────────┘
...
```

---

#### 3. Test Complete (ข้อมูลจริง + สร้าง HTML) ⭐ **แนะนำ**

```bash
# เมื่อวาน
./docker-manage.sh test complete yesterday

# วันที่กำหนด (พ.ศ.)
./docker-manage.sh test complete 15-2-69

# วันที่กำหนด (ค.ศ.)
./docker-manage.sh test complete 2026-02-15
```

**จุดประสงค์:** ทดสอบครบถ้วน - ดึงข้อมูล + สร้าง HTML + แสดง preview

**Output:**
```
╔══════════════════════════════════════════╗
║   Test Complete Report System          ║
╚══════════════════════════════════════════╝

📅 Report Date: 2026-02-15

📥 Step 1: Fetching Malicious Events...
   ✅ Found 0 malicious events

📥 Step 2: Fetching Suspicious Events...
   ✅ Found 10 suspicious events

📥 Step 3: Fetching Snip IT data...
   ✅ Fetched Snip IT data for 4 devices

📄 Step 4: Creating HTML report...
   ✅ Created: event_details_2026-02-15.html
   📦 File size: 44 KB
   📂 Location: /app/event_detail/event_details_2026-02-15.html
   🔗 Report URL: https://allevent.ifn-dtc.online/event_detail/...

📨 Step 5: Building Mattermost message...
[Preview message displayed]

✅ ทดสอบสำเร็จ!
```

**ไฟล์ที่สร้าง:**
```
/home/api/deep-api/event_detail/event_details_2026-02-15.html
```

---

## การใช้งาน Production

### 🚀 ส่งรายงานจริงไปยัง Mattermost

**⚠️ คำเตือน:** คำสั่งนี้จะส่งข้อความไปยัง Mattermost จริง!

#### Manual Send

```bash
# ส่งรายงานเมื่อวาน
./docker-manage.sh send yesterday

# ส่งรายงานวันที่กำหนด (พ.ศ.)
./docker-manage.sh send 15-2-69

# ส่งรายงานวันที่กำหนด (ค.ศ.)
./docker-manage.sh send 2026-02-15
```

**Confirmation:**
```
⚠️  Sending REAL report to Mattermost (date: yesterday)...
Are you sure? (yes/no): yes
✅ Report sent!
```

---

### 📅 Automated Daily Reports (Cron)

Services `daily-report` จะรัน cron อัตโนมัติ:

**Default:** ทุกวัน 08:00 น. (DAILY_REPORT_CRON=0 8 * * *)

#### ตรวจสอบ Cron Status

```bash
# ดู logs ของ daily-report
./docker-manage.sh logs daily-report
```

**Output ตัวอย่าง:**
```
Starting daily report cron...
Cron schedule: 0 8 * * * (08:00 AM daily)
Started daily report cron successfully
Waiting for scheduled time...

# เมื่อถึงเวลา (08:00)
[2026-02-16 08:00:01] Running daily report...
[2026-02-16 08:00:45] ✅ Report sent successfully!
```

#### เปลี่ยนเวลา Cron

แก้ไขใน `.env`:

```bash
# ตัวอย่าง: ทุกวัน 09:30 น.
DAILY_REPORT_CRON=30 9 * * *

# ตัวอย่าง: ทุกวันจันทร์ 08:00 น.
DAILY_REPORT_CRON=0 8 * * 1

# ตัวอย่าง: ทุกวัน 08:00 และ 17:00 น.
DAILY_REPORT_CRON=0 8,17 * * *
```

**จากนั้น restart:**
```bash
./docker-manage.sh restart
```

---

### 🔍 Real-time Monitor

Service `monitor` จะตรวจสอบ events แบบ real-time และส่งแจ้งเตือนทันที:

#### ตรวจสอบ Monitor Status

```bash
./docker-manage.sh logs monitor
```

**Output ตัวอย่าง:**
```
Starting continuous monitor...
Connected to Deep Instinct API
Monitoring for new events (interval: 5 minutes)...

[2026-02-16 11:45:01] Checking for new events...
[2026-02-16 11:45:03] Found 2 new malicious events
[2026-02-16 11:45:04] ✅ Alert sent to Mattermost
[2026-02-16 11:45:05] Saved to database
```

---

## Database Management

### Query Events

```bash
# แสดง events วันนี้
./docker-manage.sh query --today

# แสดง events เมื่อวาน
./docker-manage.sh query --yesterday

# แสดง events วันที่กำหนด
./docker-manage.sh query --date 2026-02-15

# แสดง malicious events อย่างเดียว
./docker-manage.sh query --date 2026-02-15 --type malicious

# แสดง statistics
./docker-manage.sh query --stats

# ค้นหาตาม keyword
./docker-manage.sh query --search "ransomware"

# แสดง events ที่ยังไม่ได้ notify
./docker-manage.sh query --unnotified

# แสดง HTML reports
./docker-manage.sh query --reports

# แสดงความช่วยเหลือ
./docker-manage.sh query --help
```

**Output ตัวอย่าง:**
```bash
./docker-manage.sh query --date 2026-02-15
```

```
Events for 2026-02-15 (Total: 10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Event ID: 15059
Type    : suspicious
Time    : 2026-02-15 13:43:52
Action  : PREVENTED
Severity: MODERATE
Device  : DESKTOP-ABC123
Status  : notified ✓

[... 9 more events ...]

Summary:
  Malicious : 0
  Suspicious: 10
  PREVENTED : 5
  DETECTED  : 5
```

---

### Database Maintenance

```bash
# Backup database
./docker-manage.sh db backup

# Optimize database (VACUUM)
./docker-manage.sh db vacuum

# Show database statistics
./docker-manage.sh db stats

# Cleanup old events (older than 90 days)
./docker-manage.sh db cleanup
```

**Output ตัวอย่าง:**
```bash
./docker-manage.sh db backup
```

```
ℹ️  Creating database backup...
✅ Backup created: /app/backups/events_backup_20260216_114500.db
📦 Size: 2.5 MB
```

```bash
./docker-manage.sh db stats
```

```
Database Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Database Path  : /app/data/events.db
Database Size  : 2.5 MB
Total Events   : 1,234
  Malicious    : 234
  Suspicious   : 1,000
Notified Events: 1,200 (97.2%)
HTML Reports   : 45
Oldest Event   : 2025-12-01
Newest Event   : 2026-02-16
```

---

## Advanced Commands

### Execute Custom Commands in Container

```bash
# รัน Python script ใดก็ได้
./docker-manage.sh exec report-server python3 custom_script.py

# เข้าไปใน shell ของ container
./docker-manage.sh shell report-server

# ดูไฟล์ใน container
./docker-manage.sh exec report-server ls -la /app/

# ตรวจสอบ database
./docker-manage.sh exec report-server python3 -c "from database import get_db; print(get_db().get_statistics())"
```

---

## Troubleshooting

### 1. Services ไม่ start

```bash
# ตรวจสอบ logs
./docker-manage.sh logs

# ตรวจสอบ .env file
cat .env | grep -v "^#" | grep -v "^$"

# Rebuild images
./docker-manage.sh rebuild
```

---

### 2. Test scripts ไม่ทำงาน

```bash
# ตรวจสอบว่า test scripts อยู่ใน container
./docker-manage.sh exec report-server ls -la /app/test*.py

# ถ้าไม่มี, rebuild
./docker-manage.sh rebuild
```

---

### 3. HTML reports ไม่แสดง

```bash
# ตรวจสอบว่าไฟล์ถูกสร้าง
./docker-manage.sh exec report-server ls -la /app/event_detail/

# ตรวจสอบ port 8080
curl http://localhost:8080

# ตรวจสอบ permissions
./docker-manage.sh exec report-server ls -ld /app/event_detail
```

---

### 4. Database errors

```bash
# ตรวจสอบ database file
./docker-manage.sh exec report-server ls -la /app/data/

# Test database connection
./docker-manage.sh exec report-server python3 -c "from database import get_db; db = get_db(); print('Database OK')"

# Backup และสร้างใหม่
./docker-manage.sh db backup
./docker-manage.sh exec report-server rm /app/data/events.db
./docker-manage.sh restart
```

---

### 5. Cron ไม่รัน

```bash
# ตรวจสอบ logs
./docker-manage.sh logs daily-report | grep -i cron

# ตรวจสอบ timezone
./docker-manage.sh exec daily-report date

# ตรวจสอบ DAILY_REPORT_CRON
grep DAILY_REPORT_CRON .env
```

---

### 6. API Connection errors

```bash
# Test API connection
./docker-manage.sh exec report-server python3 test_connection.py

# ตรวจสอบ .env
grep DEEPINSTINCT_URL .env
grep TOKENS_KEY .env

# ดู logs เต็ม
./docker-manage.sh logs report-server | grep -i error
```

---

## File Structure

```
/home/api/deep-api/
├── docker-compose.prod.yml       # Docker Compose config
├── Dockerfile                    # Docker image definition
├── docker-entrypoint.sh          # Container entrypoint
├── docker-manage.sh              # Management script ⭐
├── .env                          # Configuration
│
├── *.py                          # Python scripts (copied to container)
│   ├── test_complete_report.py   # Full test
│   ├── test_report_preview.py    # Preview test
│   ├── test_report_format.py     # Format test
│   ├── send_today_to_mattermost.py  # Production send
│   ├── deepinstinct_to_mattermost.py  # Monitor
│   ├── query_events.py           # Query tool
│   ├── db_maintenance.py         # DB maintenance
│   ├── database.py               # Database manager
│   └── serve_reports.py          # HTTP server
│
└── data/                         # Mounted volumes
    ├── event_detail/             # HTML reports
    ├── logs/                     # Log files
    ├── data/                     # SQLite database
    └── backups/                  # Database backups
```

---

## Quick Reference

### 🚀 Common Workflows

#### ทดสอบระบบ (ครั้งแรก)

```bash
./docker-manage.sh start
./docker-manage.sh test complete yesterday
```

---

#### ส่งรายงานแบบ Manual

```bash
./docker-manage.sh test complete yesterday  # ทดสอบก่อน
./docker-manage.sh send yesterday           # ส่งจริง
```

---

#### ตรวจสอบระบบประจำวัน

```bash
./docker-manage.sh status
./docker-manage.sh logs daily-report | tail -50
./docker-manage.sh db stats
```

---

#### Backup และ Maintenance

```bash
./docker-manage.sh db backup
./docker-manage.sh db vacuum
./docker-manage.sh db cleanup
```

---

#### Update Code

```bash
# แก้ไข Python files
nano send_today_to_mattermost.py

# Rebuild และ restart
./docker-manage.sh rebuild
```

---

## Summary

✅ **Services:** 3 containers (report-server, daily-report, monitor)  
✅ **Test Scripts:** 3 modes (format, preview, complete)  
✅ **Database:** SQLite with full query/maintenance tools  
✅ **Cron:** Automated daily reports  
✅ **Monitor:** Real-time alerts  
✅ **HTML Reports:** Detailed event information with Snip IT data  

**Management Script:** `docker-manage.sh` (one command for everything)

---

## Support

**Documentation:**
- `README.md` - Project overview
- `SUMMARY.md` - Complete project summary
- `README_DATABASE.md` - Database documentation
- `DOCKER_GUIDE.md` - This document
- `TEST_COMPLETE_SUMMARY.md` - Test results

**Commands:**
```bash
# Show help
./docker-manage.sh help

# View specific service logs
./docker-manage.sh logs [service]

# Get container shell
./docker-manage.sh shell report-server
```

---

**Last Updated:** 2026-02-16  
**Status:** ✅ PRODUCTION READY
