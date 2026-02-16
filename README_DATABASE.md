# Database Integration Guide

## 📋 Overview

ระบบ Deep Instinct to Mattermost ได้เพิ่ม **SQLite database** สำหรับเก็บ event history และ HTML report metadata เพื่อ:

- ✅ ป้องกันการส่ง notification ซ้ำ
- ✅ เก็บประวัติ events สำหรับ query และวิเคราะห์
- ✅ Track การส่ง notification
- ✅ จัดการ HTML reports
- ✅ สร้างรายงานและสถิติ

---

## 🗄️ Database Schema

### Tables

#### 1. **events** - เก็บ security events
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    event_id INTEGER UNIQUE NOT NULL,
    event_type TEXT NOT NULL,           -- 'malicious' หรือ 'suspicious'
    threat_type TEXT,
    threat_severity TEXT,
    action TEXT,                        -- 'DETECTED' หรือ 'PREVENTED'
    status TEXT,
    description TEXT,
    
    -- Device information
    device_name TEXT,
    hostname TEXT,
    ip_address TEXT,
    os TEXT,
    
    -- Organization
    msp_name TEXT,
    tenant_name TEXT,
    
    -- File information
    file_name TEXT,
    file_path TEXT,
    file_hash TEXT,
    container_hash TEXT,
    
    -- Snip IT integration
    responsible_person TEXT,
    department TEXT,
    division TEXT,
    
    -- Timestamps
    timestamp TEXT NOT NULL,
    recorded_device_timestamp TEXT,
    insertion_timestamp TEXT,
    created_at TEXT NOT NULL,
    
    -- Notification tracking
    notified INTEGER DEFAULT 0,
    notified_at TEXT,
    notification_count INTEGER DEFAULT 0,
    
    -- Raw data (JSON)
    raw_data TEXT
)
```

#### 2. **html_reports** - เก็บข้อมูล HTML reports
```sql
CREATE TABLE html_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    
    -- Statistics
    malicious_count INTEGER DEFAULT 0,
    suspicious_count INTEGER DEFAULT 0,
    total_events INTEGER DEFAULT 0,
    
    -- Report metadata
    generated_at TEXT NOT NULL,
    sent_to_mattermost INTEGER DEFAULT 0,
    mattermost_sent_at TEXT,
    
    -- Report URL
    report_url TEXT,
    
    UNIQUE(report_date, file_name)
)
```

#### 3. **notification_log** - เก็บประวัติการส่ง notification
```sql
CREATE TABLE notification_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    notification_type TEXT NOT NULL,    -- 'mattermost', 'email', etc.
    sent_at TEXT NOT NULL,
    success INTEGER NOT NULL,
    error_message TEXT,
    
    FOREIGN KEY (event_id) REFERENCES events(event_id)
)
```

---

## 📂 File Structure

```
deep-api/
├── database.py              # Database manager class
├── query_events.py          # Query และดูข้อมูล events
├── db_maintenance.py        # Backup, vacuum, cleanup
├── data/
│   └── events.db           # SQLite database file (auto-created)
└── backups/
    └── events_backup_*.db  # Database backups
```

---

## 🚀 Usage

### 1. Automatic Integration

Scripts หลักได้ integrate database แล้วอัตโนมัติ:

#### **send_today_to_mattermost.py**
```bash
# รันตามปกติ - จะบันทึก events ลง database อัตโนมัติ
python3 send_today_to_mattermost.py

# รายงานวันที่กำหนด
python3 send_today_to_mattermost.py 2026-02-13
```

**Features:**
- ✅ บันทึก events ทั้งหมดลง database
- ✅ จับคู่กับ Snip IT และบันทึกผู้รับผิดชอบ
- ✅ บันทึก HTML report metadata
- ✅ แสดงสถิติจาก database

#### **deepinstinct_to_mattermost.py**
```bash
# Monitor แบบต่อเนื่อง - ป้องกันส่งซ้ำด้วย database
python3 deepinstinct_to_mattermost.py
```

**Features:**
- ✅ เช็ค event ซ้ำก่อนส่ง notification
- ✅ บันทึก notification log
- ✅ Skip events ที่เคยส่งแล้ว

---

### 2. Query Events

#### **query_events.py** - ดูและค้นหา events

```bash
# แสดงสถิติทั้งหมด
python3 query_events.py --stats

# Query events วันนี้
python3 query_events.py --date today

# Query events วันที่กำหนด
python3 query_events.py --date 2026-02-13

# Query เฉพาะ malicious events
python3 query_events.py --date today --type malicious

# แสดง events ที่ยังไม่ได้ส่ง notification
python3 query_events.py --unnotified

# แสดงรายการ HTML reports
python3 query_events.py --reports

# ค้นหา events
python3 query_events.py --search "malware"
python3 query_events.py --search "Desktop-PC"

# สถิติช่วงเวลา
python3 query_events.py --stats --start-date 2026-02-01 --end-date 2026-02-13

# ลบ events เก่ากว่า 90 วัน (dry run)
python3 query_events.py --cleanup 90
```

**Output Example:**
```
╔══════════════════════════════════════════════════════════════╗
║              Deep Instinct Events Query Tool                ║
╚══════════════════════════════════════════════════════════════╝

📊 Statistics
================================================================================
Total Events: 1,234

By Type:
  malicious: 856
  suspicious: 378

By Severity:
  VERY_HIGH: 12
  HIGH: 145
  MODERATE: 567
  LOW: 510

By Action:
  DETECTED: 890
  PREVENTED: 344

Notifications:
  Notified: 1,200
  Pending: 34
```

---

### 3. Database Maintenance

#### **db_maintenance.py** - จัดการ database

```bash
# Backup database
python3 db_maintenance.py --backup

# Vacuum database (ลดขนาด)
python3 db_maintenance.py --vacuum

# วิเคราะห์ database
python3 db_maintenance.py --analyze

# Cleanup events เก่ากว่า 90 วัน (dry run)
python3 db_maintenance.py --cleanup 90 --dry-run

# Cleanup events เก่ากว่า 90 วัน (จริง)
python3 db_maintenance.py --cleanup 90

# แสดงรายการ backups
python3 db_maintenance.py --list-backups

# Full maintenance (backup + vacuum + analyze)
python3 db_maintenance.py --full
```

**Output Example:**
```
╔══════════════════════════════════════════════════════════════╗
║            Database Maintenance Tool                        ║
╚══════════════════════════════════════════════════════════════╝

Database: /home/api/deep-api/data/events.db

📊 Analyzing database...

Database Size: 45.23 MB

Table Statistics:
------------------------------------------------------------
  events: 1,234 rows
  html_reports: 15 rows
  notification_log: 1,200 rows

Events Breakdown:
------------------------------------------------------------
  malicious: 856
  suspicious: 378

Notification Status:
------------------------------------------------------------
  Notified: 1,200
  Pending: 34

Date Range:
------------------------------------------------------------
  Oldest: 2026-01-15 08:00:00
  Newest: 2026-02-13 15:30:00
```

---

## 🔧 Python API

### Using DatabaseManager in Your Code

```python
from database import get_db

# Get database instance (singleton)
db = get_db()

# Save event
event_data = {
    'id': 12345,
    'threat_type': 'MALWARE_VIRUS',
    'threat_severity': 'HIGH',
    'action': 'PREVENTED',
    # ... more fields
}

snip_it_info = {
    'responsible': 'John Doe',
    'แผนก': 'IT',
    'กอง': 'Infrastructure'
}

saved = db.save_event(event_data, 'malicious', snip_it_info)

# Check if event exists
exists = db.event_exists(12345)

# Mark as notified
db.mark_as_notified(12345, 'mattermost', success=True)

# Get unnotified events
unnotified = db.get_unnotified_events(limit=50)

# Get events by date
events = db.get_events_by_date('2026-02-13')

# Get statistics
stats = db.get_statistics(start_date='2026-02-01', end_date='2026-02-13')

# Save HTML report
db.save_html_report(
    report_date='2026-02-13',
    file_name='event_details_2026-02-13.html',
    file_path='/path/to/report.html',
    malicious_count=50,
    suspicious_count=20,
    report_url='https://allevent.ifn-dtc.online/event_detail/...'
)

# Cleanup old events
deleted = db.cleanup_old_events(days=90)
```

---

## 📊 Query Examples

### Get Events with Specific Criteria

```python
from database import get_db

db = get_db()

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # High severity events
    cursor.execute("""
        SELECT * FROM events 
        WHERE threat_severity IN ('CRITICAL', 'VERY_HIGH', 'HIGH')
        ORDER BY timestamp DESC
        LIMIT 100
    """)
    
    # Events by device
    cursor.execute("""
        SELECT * FROM events 
        WHERE device_name LIKE ?
        ORDER BY timestamp DESC
    """, ('%Desktop%',))
    
    # Events with specific file hash
    cursor.execute("""
        SELECT * FROM events 
        WHERE file_hash = ?
    """, ('abc123...',))
    
    # Daily summary
    cursor.execute("""
        SELECT 
            DATE(timestamp) as date,
            event_type,
            COUNT(*) as count
        FROM events
        GROUP BY DATE(timestamp), event_type
        ORDER BY date DESC
        LIMIT 30
    """)
```

---

## 🔄 Cron Jobs

### Automated Maintenance

เพิ่ม cron jobs สำหรับ maintenance อัตโนมัติ:

```bash
# แก้ไข crontab
crontab -e

# เพิ่ม jobs
# Backup database ทุกวันเวลา 02:00
0 2 * * * cd /home/api/deep-api && python3 db_maintenance.py --backup >> logs/db_backup.log 2>&1

# Vacuum database ทุกอาทิตย์
0 3 * * 0 cd /home/api/deep-api && python3 db_maintenance.py --vacuum >> logs/db_vacuum.log 2>&1

# Cleanup events เก่ากว่า 90 วัน ทุกเดือน
0 4 1 * * cd /home/api/deep-api && python3 db_maintenance.py --cleanup 90 >> logs/db_cleanup.log 2>&1
```

---

## 🐳 Docker Integration

Database จะถูกเก็บใน volume และ persist ข้อมูล:

### docker-compose.yml

```yaml
services:
  report-server:
    volumes:
      - ./data:/app/data:rw          # Database directory
      - ./backups:/app/backups:rw    # Backup directory
```

### Docker Commands

```bash
# Backup database จาก container
docker-compose exec report-server python3 db_maintenance.py --backup

# Query events
docker-compose exec report-server python3 query_events.py --stats

# Analyze database
docker-compose exec report-server python3 db_maintenance.py --analyze
```

---

## 🔐 Security

### Best Practices

1. **Backup Regularly**
   ```bash
   # Automated daily backup
   python3 db_maintenance.py --backup
   ```

2. **Limit Database Size**
   ```bash
   # Cleanup old data
   python3 db_maintenance.py --cleanup 90
   ```

3. **Monitor Database Size**
   ```bash
   # Check size
   python3 db_maintenance.py --analyze
   ```

4. **Protect Database File**
   ```bash
   chmod 600 data/events.db
   ```

---

## 🐛 Troubleshooting

### Database Locked

```bash
# ปิด connections ทั้งหมด
pkill -f "python.*deep"

# หรือ restart services
docker-compose restart
```

### Database Corrupted

```bash
# Restore from backup
cp backups/events_backup_YYYYMMDD_HHMMSS.db data/events.db

# หรือสร้างใหม่
rm data/events.db
python3 -c "from database import get_db; get_db()"
```

### Performance Issues

```bash
# Run VACUUM
python3 db_maintenance.py --vacuum

# Cleanup old data
python3 db_maintenance.py --cleanup 90

# Check indexes
python3 db_maintenance.py --analyze
```

---

## 📈 Performance Tips

1. **Regular VACUUM** - ลดขนาด database
2. **Cleanup Old Data** - ลบ events เก่าที่ไม่ต้องการ
3. **Use Indexes** - database มี indexes อยู่แล้ว
4. **Batch Operations** - ใช้ `save_events_batch()` แทน loop

---

## 🎯 Next Steps

### Recommended Enhancements

1. **Add More Indexes**
   ```sql
   CREATE INDEX idx_events_device ON events(device_name);
   CREATE INDEX idx_events_file_hash ON events(file_hash);
   ```

2. **Add Views**
   ```sql
   CREATE VIEW recent_critical_events AS
   SELECT * FROM events 
   WHERE threat_severity IN ('CRITICAL', 'VERY_HIGH')
   AND timestamp > datetime('now', '-7 days');
   ```

3. **Add Triggers**
   ```sql
   CREATE TRIGGER update_notification_count
   AFTER INSERT ON notification_log
   BEGIN
       UPDATE events 
       SET notification_count = notification_count + 1
       WHERE event_id = NEW.event_id;
   END;
   ```

4. **Export to Other Formats**
   - CSV export
   - JSON export
   - Excel reports

---

## 📞 Support

หากมีปัญหาหรือคำถาม:

1. ตรวจสอบ logs: `logs/db_*.log`
2. Run analyze: `python3 db_maintenance.py --analyze`
3. ดู documentation: `README.md`, `SUMMARY.md`

---

**Last Updated:** 2026-02-13  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
