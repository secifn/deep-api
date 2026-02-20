# 📖 Quick Reference - Deep API

**อัปเดต:** 2026-02-19

---

## 🚀 คำสั่งที่ใช้บ่อย

### ส่งรายงาน
```bash
# ส่งรายงานเมื่อวาน (default)
docker exec deep-api-report-server python3 send_today_to_mattermost.py

# ส่งรายงานวันที่กำหนด
docker exec deep-api-report-server python3 send_today_to_mattermost.py 2026-02-16
docker exec deep-api-report-server python3 send_today_to_mattermost.py 16-2-69
```

### ทดสอบ (ไม่ส่ง Mattermost)
```bash
# Preview ข้อความ + สร้าง HTML
docker exec deep-api-report-server python3 test_complete_report.py
docker exec deep-api-report-server python3 test_complete_report.py 2026-02-16
```

### Docker
```bash
# สถานะ
docker ps | grep deep-api

# Logs
docker logs -f deep-api-daily-report
docker logs -f deep-api-report-server

# Restart
docker-compose -f docker-compose.prod.yml restart report-server daily-report
```

---

## ⚙️ Cron Schedule

| รายการ | ค่า |
|--------|-----|
| **เวลา** | ทุกวัน 08:00 น. |
| **ข้อมูล** | รายงาน events ของ **เมื่อวาน** |
| **Config** | `DAILY_REPORT_CRON=0 8 * * *` ใน .env |

---

## 🔗 การเปลี่ยน Mattermost Webhook

1. แก้ไข `.env` → `MATTERMOST_WEBHOOK_URL=https://mm.xxx/hooks/yyy`
2. Restart: `docker-compose -f docker-compose.prod.yml restart report-server daily-report`
3. ทดสอบส่งอีกครั้ง

---

## 📄 รูปแบบรายงาน

```
รายงานเหตุการณ์วันที่: 16/02/2569 | ส่งเมื่อ: 10:11:37 (GMT+7)

📊 สรุป Events
🛡️ การดำเนินการ (DETECTED/PREVENTED)
⚠️ ระดับความรุนแรง
⚠️ พบ X เครื่องที่ไม่อยู่ใน Snip IT
📄 ดูรายละเอียด Events ทั้งหมด
⚠️ รายละเอียดเครื่องที่ไม่พบใน Snip IT
```

---

## 📁 ไฟล์สำคัญ

| ไฟล์ | หน้าที่ |
|------|---------|
| `.env` | Config (Webhook, API, Snip IT) |
| `send_today_to_mattermost.py` | ส่งรายงานจริง |
| `test_complete_report.py` | ทดสอบก่อนส่ง |

---

## 📚 เอกสารเพิ่มเติม

- `SUMMARY.md` - สรุปโครงการ
- `DOCKER_GUIDE.md` - คู่มือ Docker
- `README_DATABASE.md` - คู่มือ Database
