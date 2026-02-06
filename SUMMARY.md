# 📋 สรุปโครงการ Deep Instinct to Mattermost Integration

**วันที่สร้าง:** 2026-01-29  
**อัปเดตล่าสุด:** 2026-02-05  
**สถานะ:** ✅ พร้อมใช้งาน

---

## 🎯 วัตถุประสงค์

สร้างระบบดึงข้อมูล **Malicious** และ **Suspicious Events** จาก Deep Instinct API และส่งแจ้งเตือนไปยัง **Mattermost** webhook พร้อม:
- แสดงเวลาเป็น **GMT+7** (เวลาไทย)
- สรุป **Threat Severity**, **Actions** (DETECTED/PREVENTED), **Status**
- ไฟล์ HTML รายละเอียด (Device, IP, MSP, Tenant, Filename, File Hash)
- Link ไปยังรายละเอียด Events (Cloudflare Tunnel)
- **Cron ทุกวัน 07:00** ดึงข้อมูลย้อนหลัง 1 วัน
- ข้อมูลตรงกับ **Dashboard**

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
| **`.env1`** | เก็บ config (API Key, URL, Webhook, REPORT_SERVER_URL) | ✅ พร้อมใช้ |
| **`send_today_to_mattermost.py`** | ⭐ ส่งรายงาน Malicious + Suspicious ไป Mattermost (รองรับระบุวันที่) | ✅ พร้อมใช้ |
| **`serve_reports.py`** | HTTP server สำหรับ serve ไฟล์ HTML report (port 8080) | ✅ พร้อมใช้ |
| **`cron_daily_report.sh`** | Wrapper สำหรับ cron: ดึงข้อมูลย้อนหลัง 1 วัน | ✅ พร้อมใช้ |
| **`cron_daily_report.cron`** | ตัวอย่าง crontab (ทุกวัน 07:00) | ✅ พร้อมใช้ |
| **`event_details_YYYY-MM-DD.html`** | รายงาน HTML รายละเอียด (Device, IP, MSP, Tenant, File Hash) | ✅ สร้างอัตโนมัติ |
| **`fetch_all_today.py`** | ดึง Malicious + Suspicious ของวันนี้ + บันทึก JSON | ✅ พร้อมใช้ |
| **`test_connection.py`** | ทดสอบการเชื่อมต่อ API และ Webhook | ✅ พร้อมใช้ |
| **`fetch_events_once.py`** | ดึง events ครั้งเดียว (รองรับ --after-id) | ✅ พร้อมใช้ |
| **`fetch_events_by_time.py`** | ดึง events ตามช่วงเวลา | ✅ พร้อมใช้ |
| **`fetch_today_simple.py`** | ดึง events ของวันนี้ | ✅ พร้อมใช้ |
| **`deepinstinct_to_mattermost.py`** | Monitoring ต่อเนื่อง | ⏸️ ยังไม่เปิดใช้ |
| **`requirements.txt`** | Python dependencies | ✅ พร้อมใช้ |
| **`README_INTEGRATION.md`** | คู่มือการใช้งานฉบับเต็ม | ✅ พร้อมใช้ |
| **`README_REPORTS.md`** | คู่มือ Report + Cloudflare Tunnel | ✅ พร้อมใช้ |
| **`SUMMARY.md`** | สรุปโครงการ (ไฟล์นี้) | ✅ พร้อมใช้ |

---

### 3. 🎨 รายงาน Mattermost

#### รูปแบบรายงาน (send_today_to_mattermost.py):

```markdown
### 🔒 Deep Instinct Security Report
**วันที่:** 04/02/2026 | **เวลา:** 15:28:48 (GMT+7)

#### 📊 สรุป Events วันที่ 04/02/2026
| หมวดหมู่   | จำนวน |
| Malicious  | 73   |
| Suspicious | 36   |
| รวมทั้งหมด | 109  |

#### 🛡️ การดำเนินการ (Actions)
| DETECTED  | 80 |
| PREVENTED | 29 |

#### ⚠️ ระดับความรุนแรง (Threat Severity)
| VERY_HIGH | 2 | MODERATE | 48 | LOW | 54 | ...

📄 ดูรายละเอียด Events ทั้งหมด (link ไป HTML report)
🔗 Deep Instinct Dashboard
```

#### ไฟล์ HTML รายละเอียด (event_details_YYYY-MM-DD.html):
- **Device & User Details:** Device Name, IP Address, MSP, Tenant
- **Event Indicators:** Filename, Details, File Hash
- เข้าถึงผ่าน Cloudflare Tunnel (REPORT_SERVER_URL ใน .env1)

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

### 1. ส่งรายงานไป Mattermost (แนะนำ):
```bash
cd /home/api/DeepInstint

# ส่งรายงานวันนี้
python3 send_today_to_mattermost.py

# ส่งรายงานวันที่กำหนด (รูปแบบ YYYY-MM-DD)
python3 send_today_to_mattermost.py 2026-02-04

# ส่งรายงานวันที่กำหนด (รูปแบบ วัน-เดือน-พ.ศ. เช่น 4-2-69)
python3 send_today_to_mattermost.py 4-2-69
```

### 2. Cron – รายงานอัตโนมัติทุกวัน 07:00 (ย้อนหลัง 1 วัน):
```bash
# ติดตั้งแล้ว (ตรวจสอบด้วย crontab -l)
0 7 * * * /home/api/DeepInstint/cron_daily_report.sh >> /home/api/DeepInstint/cron_daily_report.log 2>&1

# ทดสอบรันด้วยมือ
/home/api/DeepInstint/cron_daily_report.sh
```

### 3. Report Server (สำหรับเปิดไฟล์ HTML จากภายนอก):
```bash
# เริ่ม server (bind 0.0.0.0:8080)
nohup python3 serve_reports.py > server.log 2>&1 &

# หรือใช้ start_report_server.sh
./start_report_server.sh
```
ตั้งค่า Cloudflare Tunnel ชี้ไปที่ `http://localhost:8080` แล้วใส่ URL ใน .env1 → `REPORT_SERVER_URL`

### 4. ทดสอบการเชื่อมต่อ:
```bash
python3 test_connection.py
```

### 5. ดึง events ตามช่วงเวลา / วันนี้:
```bash
python3 fetch_events_by_time.py --start-time "12:00" --end-time "15:00"
python3 fetch_today_simple.py
python3 fetch_all_today.py   # ดึงทั้งหมด + บันทึก JSON
```

### 6. ดึง events ครั้งเดียว:
```bash
python3 fetch_events_once.py
python3 fetch_events_once.py --after-id 17080 --dry-run
```

---

## ⚙️ Configuration (.env1)

```bash
# Deep Instinct API
DEEPINSTINCT_URL=https://ro.customers.deepinstinctweb.com/api/v1/
TOKENS_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Mattermost Webhook
MATTERMOST_WEBHOOK_URL=https://your-mattermost.com/hooks/xxx

# Report Server URL (สำหรับ link รายละเอียด HTML – ใช้ Cloudflare Tunnel หรือ IP:8080)
REPORT_SERVER_URL=https://allevent.ifn-dtc.online

# Polling Interval (seconds) – ใช้กับ deepinstinct_to_mattermost.py
POLLING_INTERVAL=300
```

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

### ✅ พร้อมใช้งาน:
- [x] เชื่อมต่อ Deep Instinct API
- [x] ดึงข้อมูล Malicious + Suspicious Events
- [x] ส่งรายงานไปยัง Mattermost (Threat Severity, Actions)
- [x] แสดงเวลาเป็น GMT+7 (เวลาไทย)
- [x] ไฟล์ HTML รายละเอียด (Device, IP, MSP, Tenant, Filename, File Hash)
- [x] Link ไปยังรายละเอียด (REPORT_SERVER_URL / Cloudflare Tunnel)
- [x] รองรับระบุวันที่ (YYYY-MM-DD หรือ วัน-เดือน-พ.ศ. เช่น 4-2-69)
- [x] **Cron ทุกวัน 07:00** – ดึงข้อมูลย้อนหลัง 1 วัน ส่ง Mattermost
- [x] Report Server (serve_reports.py) สำหรับ serve HTML
- [x] รองรับ Pagination และ API response แบบ dict (events/last_id)
- [x] รวม events ตาม Status และ threat_type ตรงกับ Dashboard

### ⏳ ยังไม่ได้เปิดใช้งาน:
- [ ] Monitoring อัตโนมัติทุก 5 นาที (สคริปต์: `deepinstinct_to_mattermost.py`)

---

## 🔄 การเปิดใช้งาน Monitoring (ในอนาคต)

### วิธีที่ 1: รันโดยตรง
```bash
python3 deepinstinct_to_mattermost.py
```

### วิธีที่ 2: ใช้ systemd (แนะนำ)
```bash
# ติดตั้งเป็น service
sudo bash install_service.sh

# จัดการ service
sudo systemctl start deepinstinct
sudo systemctl status deepinstinct
sudo systemctl stop deepinstinct
```

### วิธีที่ 3: ใช้ cron (รายงานรายวัน – ใช้งานอยู่)
```bash
# รายงานทุกวัน 07:00 น. (ดึงข้อมูลย้อนหลัง 1 วัน)
0 7 * * * /home/api/DeepInstint/cron_daily_report.sh >> /home/api/DeepInstint/cron_daily_report.log 2>&1
```

### วิธีที่ 4: ใช้ Docker
```bash
# สร้าง Dockerfile แล้วรัน
docker build -t deepinstinct-mattermost .
docker run -d deepinstinct-mattermost
```

---

## 📚 เอกสารเพิ่มเติม

- **`README_INTEGRATION.md`** - คู่มือการใช้งานฉบับเต็ม
- **`SwagerDeep.txt`** - Deep Instinct API Documentation (Swagger/OpenAPI)
- **`.env.example`** - ตัวอย่าง configuration file

---

## 🐛 Troubleshooting

### ปัญหา: 401 Unauthorized
**สาเหตุ:** ใช้ token ผิดประเภท  
**วิธีแก้:**
1. ไปที่ Deep Instinct UI → Settings → API Connectors
2. สร้าง API Connector ใหม่ (ถ้ายังไม่มี)
3. คัดลอก API Key (JWT token)
4. อัพเดทใน `.env1` → `TOKENS_KEY`

### ปัญหา: เวลาไม่ตรง
**สาเหตุ:** API ส่งมาเป็น UTC  
**วิธีแก้:** ใช้สคริปต์ `send_to_mattermost.py` (แปลง timezone แล้ว)

### ปัญหา: count ไม่ตรงกับ Dashboard
**สาเหตุ:** Filter ออก events ที่มี threat_type = N/A  
**วิธีแก้:** ใช้สคริปต์ `send_to_mattermost.py` เวอร์ชันล่าสุด (รวม N/A แล้ว)

### ปัญหา: ดึงแค่ 50 events
**สาเหตุ:** API มี default limit  
**วิธีแก้:** ใช้ parameter `after_event_id` เพื่อ paginate

### ปัญหา: เปิดไฟล์ HTML ไม่ได้ (502 / connection refused)
**สาเหตุ:** Report server ไม่รัน หรือ Cloudflare Tunnel ชี้ผิด  
**วิธีแก้:** รัน `python3 serve_reports.py` (หรือ nohup ใน background) และตั้ง Cloudflare Tunnel Service เป็น `http://localhost:8080`

### ปัญหา: Cron ไม่รันหรือวันที่ผิด
**สาเหตุ:** สคริปต์ส่งรูปแบบ YYYY-MM-DD; ถ้า parse ผิดจะ error  
**วิธีแก้:** ใช้ `cron_daily_report.sh` ซึ่งส่ง `date -d yesterday +%Y-%m-%d` ให้อัตโนมัติ ตรวจสอบ log: `tail -f cron_daily_report.log`

---

## 🎉 สรุป

ระบบ **Deep Instinct to Mattermost Integration** พร้อมใช้งานครบถ้วน โดยสามารถ:

✅ **ดึงข้อมูล** Malicious + Suspicious Events จาก Deep Instinct API  
✅ **ส่งรายงาน** สรุป (Threat Severity, Actions) ไปยัง Mattermost  
✅ **สร้างไฟล์ HTML** รายละเอียด (Device, IP, MSP, Tenant, Filename, File Hash)  
✅ **Link รายละเอียด** ผ่าน Cloudflare Tunnel (REPORT_SERVER_URL)  
✅ **Cron ทุกวัน 07:00** ดึงข้อมูลย้อนหลัง 1 วัน ส่ง Mattermost อัตโนมัติ  
✅ **ระบุวันที่** ได้ (YYYY-MM-DD หรือ วัน-เดือน-พ.ศ.)  
✅ **Timezone** แสดงเป็น GMT+7 (เวลาไทย)  
✅ **ข้อมูล** ตรงกับ Dashboard  

**พร้อมใช้งาน Production!** 🚀

---

## 📞 ติดต่อและสนับสนุน

หากมีปัญหาหรือข้อสงสัย:
1. อ่าน `README_INTEGRATION.md` สำหรับรายละเอียดเพิ่มเติม
2. ตรวจสอบ Troubleshooting ด้านบน
3. ทดสอบด้วย `test_connection.py` ก่อนใช้งานจริง

---

**Last Updated:** 2026-02-05  
**Version:** 2.0.0  
**Status:** ✅ Production Ready
