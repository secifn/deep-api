# Deep Instinct to Mattermost Integration

สคริปต์สำหรับดึงข้อมูล Security Events และ Suspicious Events จาก Deep Instinct API และส่งแจ้งเตือนไปยัง Mattermost webhook แบบอัตโนมัติ

## ✨ Features

- 🔄 ดึงข้อมูล Events และ Suspicious Events จาก Deep Instinct API
- 📨 ส่งแจ้งเตือนไปยัง Mattermost พร้อม format ที่สวยงาม
- 🎨 แสดงสีตามระดับความรุนแรง (Critical, High, Medium, Low)
- ⏱️ รองรับการทำงานแบบ continuous polling
- 📊 แสดงข้อมูลครบถ้วน: Device, File, Hash, Timestamp, etc.
- 🛡️ จัดการ errors และ retry อย่างเหมาะสม

## 📋 Requirements

- Python 3.7+
- Deep Instinct API Token (JWT)
- Mattermost Incoming Webhook URL

## 🚀 Installation

1. **Clone หรือ copy ไฟล์**

```bash
cd /home/api/DeepInstint
```

2. **ติดตั้ง dependencies**

```bash
pip install -r requirements.txt
```

หรือติดตั้งแบบ manual:

```bash
pip install requests python-dotenv
```

3. **ตั้งค่า Environment Variables**

แก้ไขไฟล์ `.env1` และเพิ่ม Mattermost webhook URL:

```bash
# Deep Instinct API Configuration
DEEPINSTINCT_URL=https://ro.customers.deepinstinctweb.com/api/v1/
TOKENS_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Mattermost Webhook Configuration
MATTERMOST_WEBHOOK_URL=https://your-mattermost-server.com/hooks/xxx-your-hook-id-xxx

# Polling Configuration (optional)
POLLING_INTERVAL=300  # 5 minutes
```

## 🎯 การใช้งาน

### 1. รันแบบ Continuous (Recommended)

สคริปต์จะทำงานต่อเนื่อง และตรวจสอบ events ใหม่ทุกๆ 5 นาที (หรือตามที่กำหนดใน POLLING_INTERVAL):

```bash
python deepinstinct_to_mattermost.py
```

หยุดการทำงานด้วย `Ctrl+C`

### 2. รันแบบ One-time

ถ้าต้องการรันเพียงครั้งเดียว แล้วหยุด ให้แก้ไขในไฟล์:

```python
# แทนที่บรรทัดนี้
monitor.run_continuous(interval=polling_interval)

# ด้วย
monitor.check_new_events()
```

### 3. รันด้วย systemd (Linux)

สร้างไฟล์ service:

```bash
sudo nano /etc/systemd/system/deepinstinct-monitor.service
```

เพิ่มเนื้อหา:

```ini
[Unit]
Description=Deep Instinct to Mattermost Monitor
After=network.target

[Service]
Type=simple
User=api
WorkingDirectory=/home/api/DeepInstint
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /home/api/DeepInstint/deepinstinct_to_mattermost.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

เปิดใช้งาน:

```bash
sudo systemctl daemon-reload
sudo systemctl enable deepinstinct-monitor
sudo systemctl start deepinstinct-monitor
sudo systemctl status deepinstinct-monitor
```

### 4. รันด้วย cron

เพิ่มใน crontab เพื่อรันทุก 5 นาที:

```bash
crontab -e
```

เพิ่มบรรทัด:

```
*/5 * * * * cd /home/api/DeepInstint && /usr/bin/python3 deepinstinct_to_mattermost.py >> /var/log/deepinstinct-monitor.log 2>&1
```

### 5. รันด้วย Docker (Optional)

สร้าง Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY deepinstinct_to_mattermost.py .
COPY .env1 .

CMD ["python", "deepinstinct_to_mattermost.py"]
```

Build และรัน:

```bash
docker build -t deepinstinct-monitor .
docker run -d --name deepinstinct-monitor --restart unless-stopped deepinstinct-monitor
```

## 📊 ตัวอย่าง Output ใน Mattermost

สคริปต์จะส่งข้อความที่มี format ดังนี้:

```
🚨 New Event Detected

Event ID: 12345
Type: RANSOMWARE
Severity: CRITICAL
Status: OPEN
Device: DESKTOP-ABC123
OS: WINDOWS
File Name: malicious.exe
Path: C:\Users\John\Downloads\malicious.exe
File Hash: `a1b2c3d4e5f6...`
Timestamp: 2024-01-29T10:30:00Z

Deep Instinct Security
```

## 🎨 สีตามระดับความรุนแรง

- 🔴 **CRITICAL**: สีแดง (#FF0000)
- 🟠 **HIGH**: สีส้ม (#FF6600)
- 🟡 **MEDIUM**: สีเหลือง (#FFD700)
- 🟢 **LOW**: สีเขียว (#00FF00)
- 🔵 **INFO**: สีน้ำเงิน (#0099FF)

## 🔧 Customization

### เปลี่ยนระยะเวลา Polling

แก้ไขใน `.env1`:

```bash
POLLING_INTERVAL=60  # ตรวจสอบทุก 1 นาที
POLLING_INTERVAL=600  # ตรวจสอบทุก 10 นาที
```

### กรอง Events ตามเงื่อนไข

เพิ่ม filter ในฟังก์ชัน `process_events`:

```python
def process_events(self, events: List[Dict], event_type: str = "Event") -> int:
    count = 0
    
    for event in events:
        # กรองเฉพาะ CRITICAL และ HIGH
        severity = event.get('severity', '').upper()
        if severity not in ['CRITICAL', 'HIGH']:
            continue
        
        # ... ส่วนที่เหลือ
```

### แก้ไขรูปแบบข้อความ

แก้ไขในฟังก์ชัน `format_event_message` ของ class `MattermostNotifier`

## 🐛 Troubleshooting

### ❌ Error: Missing Deep Instinct credentials

ตรวจสอบว่าไฟล์ `.env1` มี:
- `DEEPINSTINCT_URL`
- `TOKENS_KEY`

### ❌ Error: Missing MATTERMOST_WEBHOOK_URL

เพิ่ม `MATTERMOST_WEBHOOK_URL` ในไฟล์ `.env1`

### ❌ 401 Unauthorized

Token อาจหมดอายุ - ขอ Token ใหม่จาก Deep Instinct Console

### ⚠️ No new events found

- ตรวจสอบว่ามี events ใหม่ใน Deep Instinct จริงหรือไม่
- ตรวจสอบว่า Token มีสิทธิ์ READ_ONLY ขึ้นไป

### ⚠️ Cannot connect to Mattermost

- ตรวจสอบ webhook URL
- ตรวจสอบ network connectivity
- ตรวจสอบว่า webhook ยังใช้งานได้

## 📝 API Endpoints ที่ใช้

1. **GET /events/** - ดึงข้อมูล security events
2. **GET /suspicious-events/** - ดึงข้อมูล suspicious events
3. **POST /events/search** - ค้นหา events ด้วยเงื่อนไข (สามารถเพิ่มได้)
4. **GET /events/{event_id}** - ดึงรายละเอียด event (สามารถเพิ่มได้)

## 🔐 Security Best Practices

1. **อย่า commit `.env1` ไปยัง git**
   ```bash
   echo ".env1" >> .gitignore
   ```

2. **ใช้ Token ที่มีสิทธิ์น้อยที่สุดเท่าที่จำเป็น**
   - ใช้ READ_ONLY permission ถ้าไม่จำเป็นต้อง modify

3. **Rotate Token เป็นระยะ**
   - เปลี่ยน API Token ทุก 3-6 เดือน

4. **Monitor logs**
   - ตรวจสอบ logs เป็นระยะเพื่อดู errors หรือ unauthorized access

## 📞 Support

สำหรับคำถามหรือปัญหา:
1. ตรวจสอบ Deep Instinct API Documentation: https://docs.deepinstinct.com/
2. ตรวจสอบ Mattermost Webhooks: https://docs.mattermost.com/developer/webhooks-incoming.html
3. ดู logs สำหรับ error details

## 📜 License

MIT License - ใช้งานได้อย่างอิสระ

## 🙏 Credits

สร้างโดยใช้:
- Deep Instinct API (Swagger Documentation)
- Mattermost Incoming Webhooks
- Python requests library
