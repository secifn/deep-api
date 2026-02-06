# 📄 รายละเอียด Event Reports - คำแนะนำการใช้งาน

## ✨ Features

### 1. Mattermost Summary Report
- ✅ สรุป Events แบบ compact
- ✅ แยกตาม Malicious/Suspicious
- ✅ แสดง Actions (DETECTED/PREVENTED)
- ✅ แสดง Threat Severity พร้อม icons
- ✅ **ไม่มี Recent Events (Top 5)** - ตามที่ขอ
- ✅ มี Link ไปดูรายละเอียดเต็ม

### 2. HTML Detail Report
- ✅ แสดงข้อมูลครบถ้วนทุก Event
- ✅ **Device & User Details:**
  - Device Name (hostname)
  - IP Address
  - MSP Name
  - Tenant Name
- ✅ **Event Indicators:**
  - Filename (path)
  - Details (description)
  - File Hash
- ✅ Design สวยงาม responsive
- ✅ มี Badges แสดง Action และ Severity

---

## 🚀 การใช้งาน

### ขั้นตอนที่ 1: เริ่ม Report Server

```bash
# ให้สิทธิ execute
chmod +x start_report_server.sh

# เริ่ม server (รันใน background)
./start_report_server.sh &

# หรือใช้ nohup
nohup ./start_report_server.sh > server.log 2>&1 &
```

Server จะรันที่ `http://localhost:8080`

### ขั้นตอนที่ 2: ตั้งค่า Server URL

แก้ไขไฟล์ `.env1`:

```env
# เปลี่ยนจาก localhost เป็น IP จริงของ server
REPORT_SERVER_URL=http://YOUR_SERVER_IP:8080
```

**ตัวอย่าง:**
```env
REPORT_SERVER_URL=http://192.168.1.100:8080
# หรือ
REPORT_SERVER_URL=https://reports.yourdomain.com
```

### ขั้นตอนที่ 3: ส่ง Report ไปยัง Mattermost

```bash
# รันสคริปต์ส่งรายงาน
python3 send_today_to_mattermost.py
```

---

## 📋 ตัวอย่าง Output

### Mattermost Message:

```
🔒 Deep Instinct Security Report
วันที่: 03/02/2026 | เวลา: 10:59:45 (GMT+7)

📊 สรุป Events วันนี้
┌───────────┬────────┐
│ Malicious │      7 │
│ Suspicious│     22 │
│ รวม       │     29 │
└───────────┴────────┘

🛡️ การดำเนินการ (Actions)
┌──────────┬────────┐
│ DETECTED │     22 │
│ PREVENTED│      7 │
└──────────┴────────┘

⚠️ ระดับความรุนแรง (Threat Severity)
┌───────────┬────────┐
│ 🔴 VERY_HIGH │      1 │
│ 🟡 MODERATE  │     16 │
│ 🟢 LOW       │     12 │
└───────────┴────────┘

📄 ดูรายละเอียด Events ทั้งหมด
🔗 Deep Instinct Dashboard
```

### HTML Report (event_details_2026-02-03.html):

- แสดงทุก Event แบบ card layout
- แยกสีตาม Malicious (แดง) / Suspicious (เหลือง)
- มี Badges แสดง Action และ Severity
- แสดงข้อมูลครบถ้วน 3 sections:
  1. **ข้อมูลทั่วไป** - Threat Type, Details
  2. **Device & User Details** - Device Name, IP, MSP, Tenant
  3. **Event Indicators** - Filename, File Hash

---

## 🔧 การตั้งค่า Production

### ใช้ Nginx เป็น Reverse Proxy

```nginx
server {
    listen 80;
    server_name reports.yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### ใช้ systemd สำหรับ Auto-start

สร้างไฟล์ `/etc/systemd/system/deepinstinct-reports.service`:

```ini
[Unit]
Description=Deep Instinct Report Server
After=network.target

[Service]
Type=simple
User=api
WorkingDirectory=/home/api/DeepInstint
ExecStart=/usr/bin/python3 /home/api/DeepInstint/serve_reports.py
Restart=always

[Install]
WantedBy=multi-user.target
```

เริ่มใช้งาน:
```bash
sudo systemctl enable deepinstinct-reports
sudo systemctl start deepinstinct-reports
sudo systemctl status deepinstinct-reports
```

---

## 🔐 Security Considerations

### 1. ใช้ HTTPS
- ติดตั้ง SSL certificate (Let's Encrypt)
- ใช้ Nginx เป็น reverse proxy with SSL

### 2. Basic Authentication
แก้ไข `serve_reports.py` เพิ่ม authentication:

```python
class AuthHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Reports"')
        self.end_headers()
    
    def do_GET(self):
        auth_header = self.headers.get('Authorization')
        if auth_header and auth_header == 'Basic dXNlcjpwYXNzd29yZA==':  # user:password
            super().do_GET()
        else:
            self.do_AUTHHEAD()
```

### 3. Firewall Rules
```bash
# อนุญาตเฉพาะ IP ของ Mattermost server
sudo ufw allow from MATTERMOST_IP to any port 8080
```

---

## 📅 Automation

### Cron Job - ส่งรายงานทุกวัน

```bash
# แก้ไข crontab
crontab -e

# เพิ่มบรรทัด: ส่งรายงานทุกวันเวลา 09:00
0 9 * * * cd /home/api/DeepInstint && python3 send_today_to_mattermost.py >> /var/log/deepinstinct_reports.log 2>&1

# หรือทุก 2 ชั่วโมง
0 */2 * * * cd /home/api/DeepInstint && python3 send_today_to_mattermost.py >> /var/log/deepinstinct_reports.log 2>&1
```

---

## 📊 ไฟล์ที่เกี่ยวข้อง

```
DeepInstint/
├── send_today_to_mattermost.py    # สคริปต์ส่งรายงานหลัก
├── serve_reports.py                # HTTP server สำหรับ HTML reports
├── start_report_server.sh          # สคริปต์เริ่ม server
├── event_details_YYYY-MM-DD.html   # HTML reports (สร้างอัตโนมัติ)
├── .env1                           # Configuration
└── README_REPORTS.md               # เอกสารนี้
```

---

## 🐛 Troubleshooting

### ปัญหา: Link ใน Mattermost เปิดไม่ได้

**สาเหตน:** Server URL ไม่ถูกต้องหรือ server ไม่ได้รัน

**แก้ไข:**
1. ตรวจสอบว่า server รันอยู่: `ps aux | grep serve_reports`
2. ตรวจสอบ firewall: `sudo ufw status`
3. ทดสอบเปิด URL ใน browser

### ปัญหา: HTML ไม่แสดงผล

**สาเหตน:** Browser cache หรือ CORS

**แก้ไข:**
1. Hard refresh: Ctrl+F5
2. เปิด Developer Console ดู errors
3. ตรวจสอบ CORS headers ใน `serve_reports.py`

### ปัญหา: Events ไม่ครบ

**สาเหตน:** `after_event_id` ต่ำเกินไป

**แก้ไข:**
แก้ไขค่า `after_event_id` ใน `send_today_to_mattermost.py`:
```python
malicious = fetch_events_with_pagination('events', 17400)  # เพิ่มค่า
suspicious = fetch_events_with_pagination('suspicious-events', 14400)  # เพิ่มค่า
```

---

## 📞 Support

หากพบปัญหาหรือต้องการความช่วยเหลือ:
1. ตรวจสอบ logs: `tail -f /var/log/deepinstinct_reports.log`
2. ทดสอบ API: `python3 test_api.py`
3. ตรวจสอบ environment: `cat .env1`

---

**Last Updated:** 2026-02-03
**Version:** 2.0
