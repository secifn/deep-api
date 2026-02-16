# 🚀 Docker Production Deployment Summary

**วันที่:** 2026-02-13  
**สถานะ:** ✅ **Running Successfully**

---

## 📊 Services Status

### ✅ Services ที่รันอยู่

| Service | Container Name | Status | Port | Description |
|---------|---------------|--------|------|-------------|
| **report-server** | deep-api-report-server | ✅ Healthy | 8080 | HTTP server สำหรับ HTML reports |
| **monitor** | deep-api-monitor | ✅ Running | - | Real-time event monitoring |
| **daily-report** | deep-api-daily-report | ✅ Running | - | Daily report (Cron: 08:00) |

---

## 🔧 การใช้งาน

### ดูสถานะ Services

```bash
cd /home/api/deep-api
docker-compose -f docker-compose.prod.yml ps
```

### ดู Logs

```bash
# ดู logs ทั้งหมด
docker-compose -f docker-compose.prod.yml logs -f

# ดู logs แต่ละ service
docker-compose -f docker-compose.prod.yml logs -f report-server
docker-compose -f docker-compose.prod.yml logs -f monitor
docker-compose -f docker-compose.prod.yml logs -f daily-report
```

### จัดการ Services

```bash
# Stop services
docker-compose -f docker-compose.prod.yml stop

# Start services
docker-compose -f docker-compose.prod.yml start

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Stop และลบ containers
docker-compose -f docker-compose.prod.yml down

# Rebuild และ restart
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 📝 Features ที่ทำงานอยู่

### 1. **Report Server** (Port 8080)
- ✅ Serve HTML reports
- ✅ CORS enabled
- ✅ Health check: `http://localhost:8080`
- ✅ Reports: `http://localhost:8080/event_detail/`

### 2. **Monitor Service**
- ✅ Real-time event monitoring
- ✅ ป้องกันส่ง notification ซ้ำ (Database)
- ✅ บันทึก events ลง SQLite
- ✅ Polling interval: 300 seconds (5 minutes)
- ✅ Auto-restart on failure

### 3. **Daily Report Service**
- ✅ Cron schedule: 08:00 ทุกวัน
- ✅ ส่งรายงานไป Mattermost
- ✅ สร้าง HTML report
- ✅ บันทึกลง database

---

## 🗄️ Database Integration

### Database Location
```
/home/api/deep-api/data/events.db
```

### Query Events
```bash
# เข้าไปใน container
docker-compose -f docker-compose.prod.yml exec report-server bash

# Query events
python3 query_events.py --stats
python3 query_events.py --date today
python3 query_events.py --unnotified
```

### Database Maintenance
```bash
# Backup database
docker-compose -f docker-compose.prod.yml exec report-server python3 db_maintenance.py --backup

# Analyze database
docker-compose -f docker-compose.prod.yml exec report-server python3 db_maintenance.py --analyze

# Vacuum database
docker-compose -f docker-compose.prod.yml exec report-server python3 db_maintenance.py --vacuum
```

---

## 📊 Monitoring

### Health Checks

```bash
# Check container health
docker ps --filter "name=deep-api"

# Check report server
curl http://localhost:8080

# View resource usage
docker stats deep-api-report-server deep-api-monitor deep-api-daily-report
```

### Logs Location

```
/home/api/deep-api/logs/
├── daily-report.log
└── (other logs)
```

---

## 🔄 Manual Operations

### รัน Daily Report ด้วยมือ

```bash
# รายงานวันนี้
docker-compose -f docker-compose.prod.yml exec daily-report python3 send_today_to_mattermost.py

# รายงานวันที่กำหนด
docker-compose -f docker-compose.prod.yml exec daily-report python3 send_today_to_mattermost.py 2026-02-13
```

### ทดสอบการเชื่อมต่อ

```bash
docker-compose -f docker-compose.prod.yml exec monitor python3 test_connection.py
```

---

## 📂 Volumes (Data Persistence)

```
/home/api/deep-api/
├── event_detail/     # HTML reports
├── logs/             # Application logs
├── data/             # SQLite database
└── backups/          # Database backups
```

**ข้อมูลทั้งหมดจะถูกเก็บไว้แม้ restart containers**

---

## 🔐 Security Features (Production)

✅ **restart: always** - Auto-restart on failure  
✅ **security_opt: no-new-privileges** - Security hardening  
✅ **Log rotation** - Max 10MB per file, 3 files  
✅ **Health checks** - Auto-recovery  
✅ **Network isolation** - Custom bridge network  

---

## 🐛 Troubleshooting

### Services ไม่ start

```bash
# ดู logs
docker-compose -f docker-compose.prod.yml logs

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Port 8080 ถูกใช้

```bash
# หา process ที่ใช้ port
ps aux | grep serve_reports

# Kill process
kill <PID>

# Restart services
docker-compose -f docker-compose.prod.yml restart report-server
```

### Database issues

```bash
# เข้าไปใน container
docker-compose -f docker-compose.prod.yml exec report-server bash

# Check database
python3 db_maintenance.py --analyze

# Backup database
python3 db_maintenance.py --backup
```

---

## 📈 Performance

### Resource Limits (Production Config)

- **CPU**: No limit (uses available)
- **Memory**: No limit (uses available)
- **Log size**: 10MB max per file
- **Log files**: 3 files rotation

### Optimization Tips

1. **Database Vacuum** - รันทุกสัปดาห์
   ```bash
   docker-compose -f docker-compose.prod.yml exec report-server python3 db_maintenance.py --vacuum
   ```

2. **Cleanup Old Events** - รันทุกเดือน
   ```bash
   docker-compose -f docker-compose.prod.yml exec report-server python3 db_maintenance.py --cleanup 90
   ```

3. **Monitor Logs Size**
   ```bash
   du -sh logs/
   ```

---

## 🎯 Next Steps

### Recommended Actions

1. **Setup Monitoring**
   - Monitor container health
   - Setup alerts for failures
   - Track resource usage

2. **Backup Strategy**
   - Daily database backup
   - Weekly full backup
   - Off-site backup storage

3. **Security Hardening**
   - Setup firewall rules
   - Configure SSL/TLS
   - Implement rate limiting

4. **Performance Tuning**
   - Monitor database size
   - Optimize queries
   - Adjust polling intervals

---

## 📞 Quick Reference

### Start/Stop Commands

```bash
# Start
docker-compose -f docker-compose.prod.yml up -d

# Stop
docker-compose -f docker-compose.prod.yml down

# Restart
docker-compose -f docker-compose.prod.yml restart

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Status
docker-compose -f docker-compose.prod.yml ps
```

### Database Commands

```bash
# Query
docker-compose -f docker-compose.prod.yml exec report-server python3 query_events.py --stats

# Backup
docker-compose -f docker-compose.prod.yml exec report-server python3 db_maintenance.py --backup

# Maintenance
docker-compose -f docker-compose.prod.yml exec report-server python3 db_maintenance.py --full
```

---

## ✅ Verification Checklist

- [x] Services running
- [x] Report server accessible (port 8080)
- [x] Monitor service active
- [x] Daily report cron scheduled
- [x] Database initialized
- [x] Volumes mounted correctly
- [x] Health checks passing
- [x] Logs being written

---

**Status:** ✅ **All Systems Operational**  
**Last Updated:** 2026-02-13 16:30:00 (GMT+7)  
**Environment:** Production  
**Docker Compose:** docker-compose.prod.yml
