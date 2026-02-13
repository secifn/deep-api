# Quick Start Guide - Deep Instinct to Mattermost

เริ่มใช้งานภายใน 5 นาที! 🚀

## 📋 Prerequisites

- Python 3.7+
- Deep Instinct API Token
- Mattermost Incoming Webhook URL

## 🚀 Quick Setup (5 Steps)

### 1️⃣ แก้ไขไฟล์ .env1

เปิดไฟล์ `.env1` และเพิ่ม Mattermost webhook URL:

```bash
nano .env1
```

แก้ไขบรรทัดนี้:

```bash
MATTERMOST_WEBHOOK_URL=https://your-actual-mattermost-server.com/hooks/your-actual-hook-id
```

**วิธีหา Mattermost Webhook URL:**
1. ไปที่ Mattermost → Main Menu → Integrations → Incoming Webhooks
2. Click "Add Incoming Webhook"
3. เลือก Channel ที่ต้องการรับแจ้งเตือน
4. Copy URL ที่ได้

### 2️⃣ ติดตั้ง Dependencies

```bash
pip3 install -r requirements.txt
```

หรือ

```bash
pip3 install requests python-dotenv
```

### 3️⃣ ทดสอบการเชื่อมต่อ

```bash
python3 test_connection.py
```

ผลลัพธ์ที่คาดหวัง:
```
✅ Deep Instinct API: PASS
✅ Mattermost Webhook: PASS
🎉 All tests passed!
```

### 4️⃣ ส่งรายงานไป Mattermost

**ส่งรายงานวันนี้ (รวม Snip IT):**

```bash
python3 send_today_to_mattermost.py
```

**ส่งรายงานตามวันที่:**

```bash
python3 send_today_to_mattermost.py 2026-02-12
```

### 5️⃣ (ตัวเลือก) รัน Monitoring ต่อเนื่อง

**แบบ Continuous (ยังไม่เปิดใช้โดยค่าเริ่มต้น):**

```bash
python3 deepinstinct_to_mattermost.py
```

หยุดด้วย `Ctrl+C`

## 🔧 Optional: ติดตั้งเป็น Service (รันอัตโนมัติ)

ถ้าต้องการให้รันอัตโนมัติตอน boot และรันต่อเนื่อง:

```bash
sudo ./install_service.sh
```

ดู logs:

```bash
sudo journalctl -u deepinstinct-monitor -f
```

## ⚙️ Configuration

แก้ไขไฟล์ `.env1`:

```bash
# ระยะเวลาการตรวจสอบ (วินาที)
POLLING_INTERVAL=300   # 5 นาที (default)
POLLING_INTERVAL=60    # 1 นาที
POLLING_INTERVAL=600   # 10 นาที
```

## 📊 ตัวอย่างข้อความใน Mattermost

```
🚨 New Event Detected

Event ID: 12345
Type: RANSOMWARE
Severity: CRITICAL
Status: OPEN
Device: DESKTOP-PC001
OS: WINDOWS
File Name: malicious.exe
Path: C:\Users\John\Downloads\malicious.exe
File Hash: a1b2c3d4e5f6...
Timestamp: 2024-01-29T10:30:00Z

Deep Instinct Security
```

## 🆘 Troubleshooting

### ❌ "Missing MATTERMOST_WEBHOOK_URL"

→ แก้ไขไฟล์ `.env1` และเพิ่ม webhook URL

### ❌ "401 Unauthorized"

→ Token หมดอายุ - ขอ token ใหม่จาก Deep Instinct

### ⚠️ "No new events found"

→ ปกติ! หมายความว่าไม่มี events ใหม่ในขณะนี้

## 📚 ข้อมูลเพิ่มเติม

- [README_INTEGRATION.md](README_INTEGRATION.md) - คู่มือฉบับเต็ม
- [test_connection.py](test_connection.py) - ทดสอบการเชื่อมต่อ
- [send_today_to_mattermost.py](send_today_to_mattermost.py) - ส่งรายงานรายวัน (รวม Snip IT)
- [fetch_snipit_devices.py](fetch_snipit_devices.py) - ดึง/ค้นหา device จาก Snip IT

## 💡 Tips

1. **ทดสอบก่อนเสมอ** ด้วย `--dry-run`
2. **ตรวจสอบ logs** หากมีปัญหา
3. **ปรับ POLLING_INTERVAL** ตามความเหมาะสม
4. **ใช้ systemd service** สำหรับ production

## 🎯 Next Steps

1. ✅ ติดตั้งและทดสอบเรียบร้อย
2. 🔧 ปรับแต่ง POLLING_INTERVAL ตามต้องการ
3. 🚀 ติดตั้งเป็น systemd service
4. 📊 ตรวจสอบ Mattermost channel เป็นประจำ
5. 🔐 Rotate API token ทุก 3-6 เดือน

---

**มีปัญหาหรือข้อสงสัย?** ลองตรวจสอบ logs ด้วย `--help` หรืออ่าน README_INTEGRATION.md


## 🎯 Next Steps

1. ✅ ติดตั้งและทดสอบเรียบร้อย
2. 🔧 ปรับแต่ง POLLING_INTERVAL ตามต้องการ
3. 🚀 ติดตั้งเป็น systemd service
4. 📊 ตรวจสอบ Mattermost channel เป็นประจำ
5. 🔐 Rotate API token ทุก 3-6 เดือน

---

**มีปัญหาหรือข้อสงสัย?** ลองตรวจสอบ logs ด้วย `--help` หรืออ่าน README_INTEGRATION.md



## 🎯 Next Steps

1. ✅ ติดตั้งและทดสอบเรียบร้อย
2. 🔧 ปรับแต่ง POLLING_INTERVAL ตามต้องการ
3. 🚀 ติดตั้งเป็น systemd service
4. 📊 ตรวจสอบ Mattermost channel เป็นประจำ
5. 🔐 Rotate API token ทุก 3-6 เดือน

---

**มีปัญหาหรือข้อสงสัย?** ลองตรวจสอบ logs ด้วย `--help` หรืออ่าน README_INTEGRATION.md



## 🎯 Next Steps

1. ✅ ติดตั้งและทดสอบเรียบร้อย
2. 🔧 ปรับแต่ง POLLING_INTERVAL ตามต้องการ
3. 🚀 ติดตั้งเป็น systemd service
4. 📊 ตรวจสอบ Mattermost channel เป็นประจำ
5. 🔐 Rotate API token ทุก 3-6 เดือน

---

**มีปัญหาหรือข้อสงสัย?** ลองตรวจสอบ logs ด้วย `--help` หรืออ่าน README_INTEGRATION.md
