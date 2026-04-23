# 📋 สรุปโครงการ Deep Instinct to Mattermost Integration

**วันที่สร้าง:** 2026-01-29  
**อัปเดตล่าสุด:** 2026-03-06  
**สถานะ:** ✅ **Production Ready** (SQLite + Docker + Not Found Devices + Royal Reports + Reports Index)

> 📖 **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** – สรุปคำสั่งที่ใช้บ่อย และการตั้งค่า

---

## 🎯 วัตถุประสงค์

สร้างระบบดึงข้อมูล **Malicious** และ **Suspicious Events** จาก Deep Instinct API และส่งแจ้งเตือนไปยัง **Mattermost** webhook พร้อม:
- แสดงเวลาเป็น **GMT+7** (เวลาไทย)
- สรุป **Threat Severity**, **Actions** (DETECTED/PREVENTED), **Status**
- ไฟล์ HTML รายละเอียด (Device, IP, MSP, Tenant, Filename, File Hash)
- Link ไปยังรายละเอียด Events (Cloudflare Tunnel)
- **Cron ทุกวัน 08:00** ดึงข้อมูลย้อนหลัง 1 วัน (รายงานเมื่อวาน)
- ข้อมูลตรงกับ **Dashboard**

---

## 🎯 Features Overview

### ⭐ **NEW - Reports Index & Royal Devices (2026-03-06)**
- ✅ **หน้ารายงานย้อนหลัง** – เก็บ Daily-report และ เครื่องที่ไม่อยู่ใน Snipe-IT แยกหัวข้อ
- ✅ **Deep Instinct Security Report** – ลิงก์ใน Mattermost ไปยังหน้ารวมรายงาน
- ✅ **Royal Chitralada Projects** – แสดงจำนวนเครื่องโครงการส่วนพระองค์ (คลิกดูรายละเอียด)
- ✅ **ไฟล์ .md** – บันทึก YYYY-MM-DD-daily-report.md สำหรับ Raw MD
- ✅ **build_reports_index.py** – สร้าง index.html แบ่ง Daily-report / เครื่องที่ไม่อยู่ใน Snipe-IT

### ⭐ **NEW - Not Found Devices Report (2026-02-17)**
- ✅ **Device Validation** - ตรวจสอบเครื่องที่ไม่พบใน Snipe IT
- ✅ **Separate HTML Report** - รายงานแยกสำหรับเครื่องที่ไม่พบ
- ✅ **Mattermost Alert** - แสดงจำนวนเครื่องที่ไม่พบในรายงาน
- ✅ **Detailed Information** - Hostname, IP, OS, Event Type, Event ID

### ⭐ **NEW - Database Integration (2026-02-13)**
- ✅ **SQLite Database** - เก็บ event history และ HTML report metadata
- ✅ **Duplicate Prevention** - ป้องกันส่ง notification ซ้ำ
- ✅ **Query & Analytics** - ค้นหาและวิเคราะห์ events
- ✅ **Database Maintenance** - Backup, vacuum, cleanup tools
- ✅ **Notification Tracking** - ติดตามประวัติการส่งทั้งหมด

### ⭐ **NEW - Docker Production Deployment (2026-02-13)**
- ✅ **Production Config** - docker-compose.prod.yml พร้อม security hardening
- ✅ **Auto-restart** - restart: always สำหรับทุก services
- ✅ **Log Rotation** - จำกัดขนาด logs (10MB, 3 files)
- ✅ **Health Checks** - ตรวจสอบสุขภาพ containers
- ✅ **Volume Persistence** - เก็บข้อมูล database, logs, reports
- ✅ **Cron Only** - ปิด real-time monitor, ใช้ cron scheduler อย่างเดียว
- ✅ **.env Mount** - Mount .env เข้า container อ่านค่าล่าสุด (รวม MATTERMOST_WEBHOOK_URL)

---

## ✅ สิ่งที่ทำสำเร็จ

### 1. 🔐 การเชื่อมต่อ API

#### ปัญหาที่แก้ไข:
- ✅ แก้ปัญหา `401 Unauthorized` โดยใช้ **API Connector Key** แทน User Token
- ✅ ปรับ Authorization header (ไม่ต้องใช้ `Bearer` prefix)
- ✅ ทดสอบการเชื่อมต่อสำเร็จ

#### Configuration:
```bash
DEEPINSTINCT_URL=https://ro.customers.deepinstinctweb.com/api/v1
TOKENS_KEY=eyJhbGci... (API Connector Key - จาก Deep Instinct UI)
MATTERMOST_WEBHOOK_URL=https://your-mattermost.com/hooks/...
POLLING_INTERVAL=300
```

---

### 2. 📁 ไฟล์และสคริปต์ที่สร้าง

| ไฟล์ | หน้าที่ | สถานะ |
|------|---------|-------|
| **`.env`** | เก็บ config (API Key, URL, Webhook, REPORT_SERVER_URL, IT Parcel) | ✅ ตรวจสอบแล้ว พร้อมใช้ |
| **`send_today_to_mattermost.py`** | ⭐ ส่งรายงาน Malicious + Suspicious + Not Found Devices | ✅ พร้อมใช้ |
| **`deepinstinct_to_mattermost.py`** | Monitoring ต่อเนื่อง (ปิดการใช้งาน) | ⚠️ DISABLED |
| **`serve_reports.py`** | HTTP server สำหรับ serve ไฟล์ HTML report (port 8080) | ✅ พร้อมใช้ |
| **`database.py`** | ⭐ Database Manager (SQLite) | ✅ พร้อมใช้ |
| **`query_events.py`** | ⭐ Query และค้นหา events จาก database | ✅ พร้อมใช้ |
| **`db_maintenance.py`** | ⭐ Database maintenance (backup, vacuum, cleanup) | ✅ พร้อมใช้ |
| **`build_not_found_devices_html.py`** | ⭐ สร้างรายงานเครื่องที่ไม่พบใน Snipe IT | ✅ พร้อมใช้ |
| **`build_royal_devices_html.py`** | ⭐ สร้างรายงานเครื่องโครงการส่วนพระองค์ (DETECTED/PREVENTED) | ✅ พร้อมใช้ |
| **`build_reports_index.py`** | ⭐ สร้างหน้า index รายงานย้อนหลัง (Daily-report, เครื่องที่ไม่อยู่ใน Snipe-IT) | ✅ พร้อมใช้ |
| **`test_complete_report.py`** | ⭐ Test script (ไม่ส่ง Mattermost) | ✅ พร้อมใช้ |
| **`test_report_preview.py`** | Test script (preview only) | ✅ พร้อมใช้ |
| **`test_connection.py`** | ทดสอบการเชื่อมต่อ API และ Webhook | ✅ พร้อมใช้ |
| **`fetch_snipit_devices.py`** | ดึงรายการ Device + ผู้รับผิดชอบจาก Snipe IT (ค้นหา -n, -r) | ✅ พร้อมใช้ |
| **`cron_daily_report.sh`** | Wrapper สำหรับ cron: ดึงข้อมูลย้อนหลัง 1 วัน | ✅ พร้อมใช้ |
| **`docker-compose.yml`** | Docker orchestration (development) | ✅ พร้อมใช้ |
| **`docker-compose.prod.yml`** | ⭐ Docker production config (monitor disabled) | ✅ รันอยู่ |
| **`docker-manage.sh`** | ⭐ Docker management script | ✅ พร้อมใช้ |
| **`Dockerfile`** | Container image definition | ✅ พร้อมใช้ |
| **`docker-entrypoint.sh`** | Docker entrypoint script | ✅ พร้อมใช้ |
| **`Makefile`** | Quick commands | ✅ พร้อมใช้ |
| **`requirements.txt`** | Python dependencies (requests, python-dotenv, tabulate) | ✅ พร้อมใช้ |
| **`README.md`** | Overview และ quick start | ✅ อัพเดทแล้ว |
| **`README_DATABASE.md`** | ⭐ คู่มือการใช้งาน Database | ✅ พร้อมใช้ |
| **`README_INTEGRATION.md`** | คู่มือการใช้งานฉบับเต็ม | ✅ พร้อมใช้ |
| **`README_REPORTS.md`** | คู่มือ Report + Cloudflare Tunnel | ✅ พร้อมใช้ |
| **`DOCKER_RUN_SUMMARY.md`** | ⭐ สรุปการ deploy Docker production | ✅ พร้อมใช้ |
| **`DOCKER_GUIDE.md`** | ⭐ คู่มือการใช้งาน Docker | ✅ พร้อมใช้ |
| **`QUICK_REFERENCE.md`** | ⭐ สรุปคำสั่งที่ใช้บ่อย | ✅ พร้อมใช้ |
| **`SUMMARY.md`** | สรุปโครงการ (ไฟล์นี้) | ✅ อัพเดทแล้ว |
| **`event_detail/`** | โฟลเดอร์เก็บไฟล์ HTML รายละเอียด Events | ✅ สร้างอัตโนมัติ |
| **`data/`** | ⭐ โฟลเดอร์เก็บ SQLite database | ✅ สร้างอัตโนมัติ |
| **`backups/`** | ⭐ โฟลเดอร์เก็บ database backups | ✅ สร้างอัตโนมัติ |
| **`logs/`** | โฟลเดอร์เก็บ application logs | ✅ สร้างอัตโนมัติ |

---

### 3. 🎨 รายงาน Mattermost

#### รูปแบบรายงาน (send_today_to_mattermost.py):

```markdown
### 🔒 Deep Instinct Security Report

รายงานเหตุการณ์วันที่: 16/02/2569 | ส่งเมื่อ: 09:28:59 (GMT+7)

#### 📊 สรุป Events วันที่ 16/2/2569
| หมวดหมู่   | จำนวน |
| Malicious  | 78   |
| Suspicious | 45   |
| รวมทั้งหมด | 123  |

#### 🛡️ การดำเนินการ (Actions)
| Action | จำนวน/เหตุการณ์ | จำนวน/เครื่อง | เป็นเครื่องของโครงการส่วนพระองค์/จำนวน |
| DETECTED  | 47 | 37 | 5 (คลิกดูรายละเอียด) |
| PREVENTED | 76 | 22 | 1 (คลิกดูรายละเอียด) |

#### ⚠️ ระดับความรุนแรง (Threat Severity)
| MODERATE  | 61 |
| LOW       | 42 |
| HIGH      | 13 |
| VERY_HIGH | 7  |

⚠️ พบ 17 เครื่องที่ไม่อยู่ใน Snipe IT

📄 ดูรายละเอียด Events ทั้งหมด (link ไป HTML report)
⚠️ รายละเอียดเครื่องที่ไม่พบใน Snipe IT (17 เครื่อง) (link)
🔗 Deep Instinct Security Report (link ไปหน้ารวมรายงานย้อนหลัง)
🔗 Deep Instinct Dashboard
```

#### ไฟล์ HTML รายละเอียด:

**1. event_details_YYYY-MM-DD.html:**
- **Device & User Details:** Device Name, IP Address, MSP, Tenant
- **จาก Snipe IT (IT Parcel):** ผู้รับผิดชอบ, แผนก, กอง (จับคู่ตาม Device Name)
- **Event Indicators:** Filename, Details, File Hash
- เมื่อไม่พบเครื่องใน Snipe IT แสดงข้อความ **"ไม่พบข้อมูลใน Snipe IT"**

**2. not_found_devices_YYYY-MM-DD.html:** ⭐ **ใหม่**
- รายการเครื่องที่ไม่พบใน Snipe IT
- แสดง: Hostname, IP Address, OS, Event Type, Event ID, Timestamp
- ตารางสวยงาม พร้อม alert banner
- เข้าถึงผ่าน Cloudflare Tunnel (REPORT_SERVER_URL ใน .env)

---

### 4. 🔧 การแก้ไขปัญหาสำคัญ

#### ปัญหาที่พบและวิธีแก้:

| ปัญหา | สาเหตุ | วิธีแก้ | สถานะ |
|-------|--------|---------|-------|
| **401 Unauthorized** | ใช้ User Token แทน API Connector Key | ใช้ API Key จาก API Connectors ใน Deep Instinct UI | ✅ แก้แล้ว |
| **Authorization header** | ใช้ `Bearer` prefix | ลบ `Bearer` ออก ใช้แค่ token เปล่าๆ | ✅ แก้แล้ว |
| **เวลาไม่ตรง (-7 ชม)** | API ส่งมาเป็น UTC (GMT+0) | แปลงเป็น GMT+7 (Bangkok timezone) | ✅ แก้แล้ว |
| **REOPEN count ผิด** | Event ID 17091 มี threat_type = N/A ถูก filter ออก | รวม REOPEN events ทั้งหมด (ไม่ว่า threat_type) | ✅ แก้แล้ว |
| **OPEN count ผิด** | Event ID 17102, 17103 มี threat_type = N/A ถูก filter ออก | รวม OPEN events ทั้งหมด (ไม่ว่า threat_type) | ✅ แก้แล้ว |
| **ดึงแค่ 50 events** | API default limit = 50 | ใช้ `after_event_id` parameter เพื่อ paginate | ✅ แก้แล้ว |

---

## 📊 ข้อมูลที่ตรวจสอบแล้ว (วันนี้ 2026-01-29)

### ตรวจสอบความถูกต้อง:

```
✅ Total Events: 44
   - OPEN: 36 (ตรงกับ Dashboard ✅)
   - CLOSED: 6
   - REOPEN: 2 (ตรงกับ Dashboard ✅)

🎯 Threat Types:
   - MALWARE_VIRUS: 24
   - MALWARE_DROPPER: 8
   - PUA_RISKWARE_HACKTOOL: 5
   - N/A: 3 (รวม: REOPEN 1 + OPEN 2)
   - MALWARE_WORM: 1
   - PUA_ADWARE: 1
   - MALWARE_BACKDOOR: 1
   - PUA_GENERIC_PUA: 1
```

### Events ที่ต้องรวม (มี threat_type = N/A):
- **[17091]** 09:58:35 - REOPEN - E:\MUSIC KERK (16GB).lnk
- **[17102]** 13:52:38 - OPEN - E:\IPALM_DRIVE (1GB).lnk
- **[17103]** 14:09:00 - OPEN - E:\Removable Drive (8GB).lnk

---

## 🚀 วิธีใช้งาน

### 🐳 Docker Production (แนะนำ - รันอยู่แล้ว):

```bash
cd /home/api/deep-api

# ดูสถานะ services
docker ps | grep deep-api

# ส่งรายงานด้วยมือ (ระบุวันที่ชัดเจน)
docker exec deep-api-report-server python3 send_today_to_mattermost.py 2026-02-16
docker exec deep-api-report-server python3 send_today_to_mattermost.py 16-2-69

# ดู logs
docker logs -f deep-api-daily-report
docker logs -f deep-api-report-server

# Query events จาก database
docker exec deep-api-report-server python3 query_events.py --stats
docker exec deep-api-report-server python3 query_events.py --date 2026-02-16

# Backup database
docker exec deep-api-report-server python3 db_maintenance.py backup

# ใช้ management script (แนะนำ)
./docker-manage.sh status
./docker-manage.sh test complete 2026-02-16
./docker-manage.sh logs
```

### 💻 Manual (ถ้าไม่ใช้ Docker):

```bash
cd /home/api/deep-api

# ส่งรายงานวันนี้
python3 send_today_to_mattermost.py

# ส่งรายงานวันที่กำหนด (รูปแบบ YYYY-MM-DD)
python3 send_today_to_mattermost.py 2026-02-04

# ส่งรายงานวันที่กำหนด (รูปแบบ วัน-เดือน-พ.ศ. เช่น 4-2-69)
python3 send_today_to_mattermost.py 4-2-69

# Query events
python3 query_events.py --stats
python3 query_events.py --date today
```

### 2. Cron – รายงานอัตโนมัติทุกวัน 08:00 (Docker):
```bash
# Docker: Cron รันอัตโนมัติใน container daily-report
# Schedule: 0 8 * * * = ทุกวัน 08:00 น.
# รายงาน: events ของเมื่อวาน (ย้อนหลัง 1 วัน)
# กำหนดใน .env: DAILY_REPORT_CRON=0 8 * * *

# ดู logs
docker logs -f deep-api-daily-report

# ทดสอบส่งด้วยมือ (รายงานเมื่อวาน)
docker exec deep-api-report-server python3 send_today_to_mattermost.py
```

### 3. Report Server (สำหรับเปิดไฟล์ HTML จากภายนอก):
```bash
# เริ่ม server (bind 0.0.0.0:8080)
nohup python3 serve_reports.py > server.log 2>&1 &

# หรือใช้ start_report_server.sh
./start_report_server.sh
```
ตั้งค่า Cloudflare Tunnel ชี้ไปที่ `http://localhost:8080` แล้วใส่ URL ใน .env1 → `REPORT_SERVER_URL`  
ลิงก์รายงาน: `{REPORT_SERVER_URL}/event_detail/event_details_YYYY-MM-DD.html`  
หน้ารวมรายงาน: `{REPORT_SERVER_URL}/event_detail/` (Daily-report, เครื่องที่ไม่อยู่ใน Snipe-IT)

### 4. ทดสอบการเชื่อมต่อ:
```bash
python3 test_connection.py
```

### 5. ดึง/ค้นหา device จาก Snipe IT:
```bash
python3 fetch_snipit_devices.py
python3 fetch_snipit_devices.py -n Desktop -r "กองศิลปาชีพ"
```

---

## ⚙️ Configuration (.env)

```bash
# Deep Instinct API
DEEPINSTINCT_URL=https://ro.customers.deepinstinctweb.com/api/v1/
TOKENS_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Mattermost Webhook
MATTERMOST_WEBHOOK_URL=https://mm.trd-dtc.one/hooks/...

# Report Server URL (สำหรับ link รายละเอียด HTML – ใช้ Cloudflare Tunnel หรือ IP:8080)
REPORT_SERVER_URL=https://allevent.ifn-dtc.online

# Polling Interval (seconds) – ใช้กับ deepinstinct_to_mattermost.py
POLLING_INTERVAL=300

# Snipe IT / IT Parcel API (Asset)
IT_PARCEL_API_URL=https://asset.trd-dtc.one/api/v1
IT_PARCEL_TOKEN=eyJ0eXAi... (JWT จาก IT Parcel)

# Daily Report Cron (Docker)
DAILY_REPORT_CRON=0 8 * * *

# Report Server Port (Docker)
REPORT_SERVER_PORT=8080
```

### ✅ การตรวจสอบ .env (2026-02-19)
- ตัวแปรครบ: DEEPINSTINCT_URL, TOKENS_KEY, MATTERMOST_WEBHOOK_URL, REPORT_SERVER_URL, POLLING_INTERVAL, IT_PARCEL_API_URL, IT_PARCEL_TOKEN
- **IT_PARCEL_API_URL** ใช้ `https://asset.trd-dtc.one/api/v1`
- **.env ใช้ env_file** – ไม่ mount เข้า container (ปลอดภัยกว่า) เปลี่ยน config ต้อง restart

### 🔄 การเปลี่ยน Mattermost Webhook URL
1. แก้ไขไฟล์ `.env` → เปลี่ยนค่า `MATTERMOST_WEBHOOK_URL`
2. Restart containers: `docker-compose -f docker-compose.prod.yml restart report-server daily-report`
3. ทดสอบส่ง: `docker exec deep-api-report-server python3 send_today_to_mattermost.py`

### ⚠️ หมายเหตุสำคัญ:
1. **`TOKENS_KEY`** = API Connector Key (ไม่ใช่ User Token)
   - หาได้จาก: Deep Instinct UI → Settings → API Connectors
   - มี format: `eyJhbGci...` (JWT token)
   
2. **Authorization Header** = ใช้ token โดยตรง (ไม่ต้องใส่ `Bearer`)
   ```python
   headers = {'Authorization': token}  # ✅ ถูก
   headers = {'Authorization': f'Bearer {token}'}  # ❌ ผิด
   ```

3. **Timezone** = API ส่งมาเป็น UTC, ต้องแปลงเป็น GMT+7 ในโค้ด

---

## 📦 Dependencies

### ติดตั้ง:
```bash
pip3 install -r requirements.txt
```

### รายการ dependencies:
```
requests>=2.31.0
python-dotenv>=1.0.0
```

---

## 💡 เทคนิคสำคัญ

### 1. Pagination (ดึง events มากกว่า 50)
```python
# ใช้ after_event_id เพื่อดึง events ใหม่ๆ
params = {"after_event_id": 17080}
response = requests.get(url, headers={'Authorization': token}, params=params)
```

### 2. Timezone Conversion (UTC → GMT+7)
```python
from datetime import datetime, timezone, timedelta

TZ_BANGKOK = timezone(timedelta(hours=7))

def convert_to_bangkok_time(iso_timestamp):
    dt_utc = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    dt_bangkok = dt_utc.astimezone(TZ_BANGKOK)
    return dt_bangkok
```

### 3. Filter Logic (รวม OPEN/REOPEN ทั้งหมด)
```python
# รวม events ที่มี threat_type หรือ status = OPEN/REOPEN
malicious = [
    e for e in today_events 
    if (e.get('threat_type') and e.get('threat_type') != 'N/A') 
    or (e.get('status') in ['OPEN', 'REOPEN'])
]
```

### 4. Sorting (เรียงตาม timestamp)
```python
# เรียงจากล่าสุดมาก่อน
recent_5 = sorted(
    malicious,
    key=lambda x: x['_bangkok_time'],
    reverse=True  # ล่าสุดมาก่อน
)[:5]
```

---

## 🎯 สถานะปัจจุบัน

### ✅ พร้อมใช้งาน Production:
- [x] เชื่อมต่อ Deep Instinct API
- [x] ดึงข้อมูล Malicious + Suspicious Events
- [x] ส่งรายงานไปยัง Mattermost (Threat Severity, Actions)
- [x] แสดงเวลาเป็น GMT+7 (เวลาไทย)
- [x] ไฟล์ HTML รายละเอียด (Device, IP, MSP, Tenant, Filename, File Hash)
- [x] Link ไปยังรายละเอียด (REPORT_SERVER_URL / Cloudflare Tunnel)
- [x] รองรับระบุวันที่ (YYYY-MM-DD หรือ วัน-เดือน-พ.ศ. เช่น 4-2-69)
- [x] **Cron ทุกวัน 08:00** – ดึงข้อมูลย้อนหลัง 1 วัน ส่ง Mattermost (Docker)
- [x] Report Server (port 8080) สำหรับ serve HTML (Docker)
- [x] รองรับ Pagination และ API response แบบ dict (events/last_id)
- [x] รวม events ตาม Status และ threat_type ตรงกับ Dashboard
- [x] **Snipe IT / IT Parcel** – จับคู่ Event กับเครื่องใน Snipe IT แสดง **ผู้รับผิดชอบ, แผนก, กอง**
- [x] แสดง **"ไม่พบข้อมูลใน Snipe IT"** เมื่อเครื่องไม่มีใน Snipe IT
- [x] **fetch_snipit_devices.py** – ดึง/ค้นหา device ตามชื่อเครื่องและผู้รับผิดชอบ

### ⭐ NEW - Database & Production (2026-02-13):
- [x] **SQLite Database** – เก็บ event history, HTML reports, notification log
- [x] **Duplicate Prevention** – ป้องกันส่ง notification ซ้ำ
- [x] **Query Tools** – query_events.py สำหรับค้นหาและวิเคราะห์
- [x] **Database Maintenance** – db_maintenance.py สำหรับ backup, vacuum, cleanup
- [x] **Docker Production** – รันด้วย docker-compose.prod.yml
- [x] **Daily Report** – Cron ทุกวัน 08:00 น. (Docker)
- [x] **Auto-restart** – Services restart อัตโนมัติเมื่อ fail
- [x] **Health Checks** – ตรวจสอบสุขภาพ containers
- [x] **Log Rotation** – จำกัดขนาด logs (10MB, 3 files)
- [x] **Volume Persistence** – เก็บข้อมูล database, logs, reports ถาวร

### ⭐ NEW - Not Found Devices (2026-02-17):
- [x] **Device Validation** – ตรวจสอบเครื่องที่ไม่พบใน Snipe IT
- [x] **Not Found Report** – สร้างรายงาน HTML แยกสำหรับเครื่องที่ไม่พบ
- [x] **Alert in Message** – แสดง "⚠️ พบ X เครื่องที่ไม่อยู่ใน Snipe IT" ในรายงาน
- [x] **Detailed Link** – ลิงก์ไปยังรายงานเครื่องที่ไม่พบ
- [x] **Pagination Fix** – เพิ่ม max_pages จาก 20 → 50 (ดึงข้อมูลครบถ้วน)

### ⭐ NEW - Reports Index & Royal Devices (2026-03-06):
- [x] **หน้ารายงานย้อนหลัง** – `event_detail/index.html` แบ่งหัวข้อ Daily-report และ เครื่องที่ไม่อยู่ใน Snipe-IT
- [x] **Deep Instinct Security Report** – ลิงก์ใน Mattermost → หน้ารวมรายงาน
- [x] **Royal Chitralada Projects** – คอลัมน์ "เป็นเครื่องของโครงการส่วนพระองค์" (DETECTED/PREVENTED แยกไฟล์)
- [x] **ไฟล์ .md** – บันทึก `YYYY-MM-DD-daily-report.md` สำหรับ Raw MD
- [x] **จำนวนเครื่อง** – รวม Malicious + Suspicious ตาม Device Name (ตรงกับ Export)

---

## 🔄 Monitoring & Services (รันอยู่แล้ว)

### ✅ Docker Production (ใช้งานอยู่):

```bash
cd /home/api/deep-api

# ดูสถานะ
docker ps | grep deep-api

# Services ที่รันอยู่:
# - report-server (port 8080) - HTTP server
# - daily-report - Daily report (cron 08:00)
# - monitor - DISABLED (ปิดการใช้งาน)

# ดู logs
docker logs -f deep-api-daily-report
docker logs -f deep-api-report-server

# Restart services
docker-compose -f docker-compose.prod.yml restart report-server daily-report

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### 📊 Database Operations:

```bash
# Query events
docker-compose -f docker-compose.prod.yml exec report-server python3 query_events.py --stats
docker-compose -f docker-compose.prod.yml exec report-server python3 query_events.py --date today

# Backup database
docker-compose -f docker-compose.prod.yml exec report-server python3 db_maintenance.py --backup

# Analyze database
docker-compose -f docker-compose.prod.yml exec report-server python3 db_maintenance.py --analyze
```

---

## 📚 เอกสารเพิ่มเติม

- **`README.md`** - Overview และ quick start
- **`QUICK_REFERENCE.md`** - ⭐ สรุปคำสั่งที่ใช้บ่อยและขั้นตอนสำคัญ
- **`README_DATABASE.md`** - ⭐ คู่มือการใช้งาน Database (SQLite)
- **`README_INTEGRATION.md`** - คู่มือการใช้งานฉบับเต็ม
- **`README_REPORTS.md`** - คู่มือ Report System
- **`DOCKER_RUN_SUMMARY.md`** - ⭐ สรุปการ deploy Docker production
- **`DEPLOYMENT.md`** - Production deployment guide
- **`ROADMAP.md`** - แผนพัฒนาต่อ
- **`SwagerDeep.json`** - Deep Instinct API Documentation (Swagger/OpenAPI)

---

## 🐛 Troubleshooting

### ปัญหา: 401 Unauthorized
**สาเหตุ:** ใช้ token ผิดประเภท  
**วิธีแก้:**
1. ไปที่ Deep Instinct UI → Settings → API Connectors
2. สร้าง API Connector ใหม่ (ถ้ายังไม่มี)
3. คัดลอก API Key (JWT token)
4. อัพเดทใน `.env` → `TOKENS_KEY`

### ปัญหา: เวลาไม่ตรง
**สาเหตุ:** API ส่งมาเป็น UTC  
**วิธีแก้:** สคริปต์ `send_today_to_mattermost.py` แปลง timezone เป็น GMT+7 แล้ว

### ปัญหา: count ไม่ตรงกับ Dashboard
**สาเหตุ:** Filter ออก events ที่มี threat_type = N/A  
**วิธีแก้:** ใช้สคริปต์ `send_today_to_mattermost.py` (รวม N/A และ Snipe IT แล้ว)

### ปัญหา: ดึงแค่ 50 events
**สาเหตุ:** API มี default limit  
**วิธีแก้:** ใช้ parameter `after_event_id` เพื่อ paginate

### ปัญหา: เปิดไฟล์ HTML ไม่ได้ (502 / connection refused)
**สาเหตุ:** Report server ไม่รัน หรือ Cloudflare Tunnel ชี้ผิด  
**วิธีแก้:** รัน `python3 serve_reports.py` (หรือ nohup ใน background) และตั้ง Cloudflare Tunnel Service เป็น `http://localhost:8080`

### ปัญหา: Cron ไม่รันหรือวันที่ผิด
**สาเหตุ:** Container daily-report รัน cron ภายใน  
**วิธีแก้:** ตรวจสอบ logs ด้วย `docker logs deep-api-daily-report`; Cron ส่งรายงานเมื่อวานอัตโนมัติ (ไม่ต้องส่ง argument)

### ปัญหา: ส่งไป Mattermost channel เดิม (เปลี่ยน webhook แล้วยังไม่เปลี่ยน)
**สาเหตุ:** ค่าเก่ายังอยู่ใน environment  
**วิธีแก้:** แก้ `.env` แล้ว restart: `docker-compose -f docker-compose.prod.yml restart report-server daily-report`

---

## 📌 ความคืบหน้า Snipe IT / IT Parcel (สรุป)

### สิ่งที่ทำแล้ว

| รายการ | รายละเอียด |
|--------|-------------|
| **การจับคู่** | Event จาก Deep Instinct จับคู่กับ Snipe IT ตาม **Device Name** (hostname) |
| **รายงาน HTML** | แต่ละ Event แสดง **ผู้รับผิดชอบ (Snipe IT)**, **แผนก (Snipe IT)**, **กอง (Snipe IT)** |
| **แหล่งข้อมูล** | ใช้ custom field **Device Name** ใน Snipe IT (และ name, asset_tag, hostname, serial, custom_fields อื่น) |
| **Search API** | เครื่องที่ไม่อยู่ใน list ใช้ **GET /hardware?search=hostname** เพื่อหาจาก Snipe IT (รองรับ custom field) |
| **ข้อความเมื่อไม่พบ** | ถ้าไม่พบเครื่องใน Snipe IT แสดง **"ไม่พบข้อมูลใน Snipe IT"** แทน N/A (ทั้งผู้รับผิดชอบ, แผนก, กอง) |
| **สคริปต์แยก** | **fetch_snipit_devices.py** – ดึงรายการ hardware + ผู้รับผิดชอบ, ค้นหาด้วย `-n` (ชื่อเครื่อง) และ `-r` (ผู้รับผิดชอบ) |

### Config ที่ใช้ (.env1)

- `IT_PARCEL_API_URL=https://asset.trd-dtc.one/api/v1`
- `IT_PARCEL_TOKEN=` (JWT จาก Snipe IT)

### วิธีทดสอบ

```bash
# สร้างรายงาน (รวม Snipe IT)
python3 send_today_to_mattermost.py 2026-02-12

# ดึงรายการ device จาก Snipe IT / ค้นหา
python3 fetch_snipit_devices.py
python3 fetch_snipit_devices.py -n Desktop -r "กองศิลปาชีพ"
```

---

## 🎉 สรุป

ระบบ **Deep Instinct to Mattermost Integration** พร้อมใช้งาน **Production** ครบถ้วน โดยสามารถ:

### Core Features:
✅ **ดึงข้อมูล** Malicious + Suspicious Events จาก Deep Instinct API  
✅ **ส่งรายงาน** สรุป (Threat Severity, Actions) ไปยัง Mattermost  
✅ **สร้างไฟล์ HTML** รายละเอียด (Device, IP, MSP, Tenant, Filename, File Hash)  
✅ **Link รายละเอียด** ผ่าน Cloudflare Tunnel (REPORT_SERVER_URL)  
✅ **Timezone** แสดงเป็น GMT+7 (เวลาไทย)  
✅ **ข้อมูล** ตรงกับ Dashboard  
✅ **Snipe IT / IT Parcel** – จับคู่ Device Name แสดง ผู้รับผิดชอบ, แผนก, กอง  

### ⭐ NEW - Database & Production:
✅ **SQLite Database** – เก็บ event history และ HTML report metadata  
✅ **Duplicate Prevention** – ป้องกันส่ง notification ซ้ำอัตโนมัติ  
✅ **Query & Analytics** – ค้นหาและวิเคราะห์ events ได้  
✅ **Database Maintenance** – Backup, vacuum, cleanup tools  
✅ **Docker Production** – รันด้วย docker-compose.prod.yml  
✅ **Real-time Monitoring** – deepinstinct_to_mattermost.py รันใน Docker (ทุก 5 นาที)  
✅ **Daily Report** – Cron ทุกวัน 08:00 น. (Docker)  
✅ **Auto-restart** – Services restart อัตโนมัติเมื่อ fail  
✅ **Health Checks** – ตรวจสอบสุขภาพ containers  
✅ **Log Rotation** – จำกัดขนาด logs (10MB, 3 files)  

**🚀 พร้อมใช้งาน Production แล้ว!**  
**📊 Docker Services: report-server, monitor, daily-report - Running**  
**🗄️ Database: SQLite with event history and analytics**

---

## 📞 ติดต่อและสนับสนุน

หากมีปัญหาหรือข้อสงสัย:
1. อ่าน `README_INTEGRATION.md` สำหรับรายละเอียดเพิ่มเติม
2. ตรวจสอบ Troubleshooting ด้านบน
3. ทดสอบด้วย `test_connection.py` ก่อนใช้งานจริง

---

**Last Updated:** 2026-03-06  
**Version:** 4.2.0  
**Status:** ✅ **Production Running** (Deep Instinct + Snipe IT + SQLite + Reports Index + Royal Devices)  
**Docker Services:** ✅ report-server, ✅ daily-report  
**Database:** ✅ SQLite (events.db) with query & maintenance tools  
**Reports:** ✅ event_detail/ (index, event_details, not_found, royal_devices, daily-report.md)
