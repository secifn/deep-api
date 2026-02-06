#!/usr/bin/env python3
"""
ส่ง Malicious Events Report ไปยัง Mattermost
แสดงเวลาเป็น GMT+7 (เวลาไทย)
"""

from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone, timedelta
import json

load_dotenv('.env1')

token = os.getenv('TOKENS_KEY')
base_url = os.getenv('DEEPINSTINCT_URL').rstrip('/')
webhook_url = os.getenv('MATTERMOST_WEBHOOK_URL')

# Timezone สำหรับประเทศไทย (GMT+7)
TZ_BANGKOK = timezone(timedelta(hours=7))

# ไฟล์สำหรับเก็บ last_event_id
LAST_ID_FILE = '/home/api/DeepInstint/.last_event_id'

def convert_to_bangkok_time(iso_timestamp):
    """แปลง ISO timestamp จาก UTC เป็นเวลาไทย (GMT+7)"""
    if not iso_timestamp:
        return None
    
    # Parse ISO format และแปลงเป็น Bangkok time
    dt_utc = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    dt_bangkok = dt_utc.astimezone(TZ_BANGKOK)
    return dt_bangkok

print("╔══════════════════════════════════════════════════════════════╗")
print("║   ส่ง Malicious Events ไปยัง Mattermost (GMT+7)            ║")
print("╚══════════════════════════════════════════════════════════════╝")
print()

# 1. ดึง Events ของวันนี้
print("📥 กำลังดึง events...")

# อ่าน last_event_id จากไฟล์ (ถ้ามี)
last_event_id = None
if os.path.exists(LAST_ID_FILE):
    try:
        with open(LAST_ID_FILE, 'r') as f:
            data = json.load(f)
            last_event_id = data.get('last_event_id')
            print(f"   อ่าน last_event_id จากไฟล์: {last_event_id}")
    except Exception as e:
        print(f"   ⚠️  ไม่สามารถอ่านไฟล์ last_event_id: {e}")

# ถ้าไม่มี last_event_id (ครั้งแรก) ให้ใช้ค่าที่ครอบคลุม 7 วันล่าสุด
if last_event_id is None:
    # สมมติ 1 วัน ~50 events, 7 วัน ~350 events
    # ใช้ค่าที่ปลอดภัย: event_id_ปัจจุบัน - 500
    last_event_id = 17000  # ค่า safe สำหรับ recent events (ปรับตามความเหมาะสม)
    print(f"   ครั้งแรก: ใช้ after_event_id = {last_event_id}")

print(f"   ดึง events หลัง ID {last_event_id}...")
url = f"{base_url}/events/"

# ดึงหลายรอบจนครบ (pagination)
all_events = []
current_after_id = last_event_id
max_pages = 10  # จำกัดไม่ให้ดึงเกิน 10 รอบ (500 events)

for page in range(max_pages):
    params = {"after_event_id": current_after_id}
    response = requests.get(url, headers={'Authorization': token}, params=params, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        exit(1)
    
    result = response.json()
    if isinstance(result, dict):
        events_batch = result.get('events', [])
    else:
        events_batch = result
    
    if not events_batch:
        # ไม่มี events เพิ่มแล้ว
        break
    
    all_events.extend(events_batch)
    
    # หา max event ID ใน batch นี้
    batch_max_id = current_after_id
    for event in events_batch:
        event_id = event.get('id')
        if event_id and event_id > batch_max_id:
            batch_max_id = event_id
    
    # ถ้า max_id ไม่เพิ่มขึ้น แสดงว่าไม่มี events ใหม่
    if batch_max_id == current_after_id:
        break
    
    current_after_id = batch_max_id
    
    # ถ้าดึงน้อยกว่า 50 แสดงว่าหมดแล้ว
    if len(events_batch) < 50:
        break

events = all_events
print(f"   ✅ ดึงได้ทั้งหมด: {len(events)} events")

# หา max event ID เพื่อบันทึกไว้ใช้ครั้งหน้า
max_event_id = last_event_id
if events:
    for event in events:
        event_id = event.get('id')
        if event_id and event_id > max_event_id:
            max_event_id = event_id
    
    # บันทึก max_event_id ลงไฟล์
    try:
        with open(LAST_ID_FILE, 'w') as f:
            json.dump({'last_event_id': max_event_id, 'updated_at': datetime.now().isoformat()}, f)
        print(f"   ✅ บันทึก last_event_id: {max_event_id}")
    except Exception as e:
        print(f"   ⚠️  ไม่สามารถบันทึก last_event_id: {e}")

# Filter วันนี้ (ใช้เวลาไทย)
now_bangkok = datetime.now(TZ_BANGKOK)
today_str = now_bangkok.strftime('%Y-%m-%d')
today_events = []

for event in events:
    ts = event.get('timestamp') or event.get('recorded_device_timestamp')
    if ts:
        try:
            dt_bangkok = convert_to_bangkok_time(ts)
            if dt_bangkok and dt_bangkok.strftime('%Y-%m-%d') == today_str:
                # เพิ่ม field สำหรับเวลาไทย
                event['_bangkok_time'] = dt_bangkok
                today_events.append(event)
        except Exception as e:
            print(f"⚠️  Warning: Cannot parse timestamp {ts}: {e}")

# Filter: รวมทั้ง threat_type, OPEN, และ REOPEN events
malicious = [
    e for e in today_events 
    if (e.get('threat_type') and e.get('threat_type') != 'N/A') 
    or (e.get('status') in ['OPEN', 'REOPEN'])
]

print(f"✅ พบ {len(malicious)} malicious events ของวันนี้")
print()

if len(malicious) == 0:
    print("ℹ️  ไม่มี malicious events ในวันนี้")
    exit(0)

# 2. นับตาม Threat Type
threat_counts = {}
for event in malicious:
    threat = event.get('threat_type', 'N/A')
    threat_counts[threat] = threat_counts.get(threat, 0) + 1

# 3. สร้าง Message สำหรับ Mattermost
message = {
    "text": "## 🚨 Deep Instinct - Malicious Events Report\n\n"
}

# Header (ใช้เวลาไทย)
message["text"] += f"**📅 Date:** {now_bangkok.strftime('%Y-%m-%d %H:%M:%S')} (GMT+7)\n"
message["text"] += f"**📊 Total Events:** {len(malicious)}\n\n"

# Threat Type Summary
message["text"] += "### 🎯 Threat Types:\n\n"
for threat, count in sorted(threat_counts.items(), key=lambda x: x[1], reverse=True):
    icon = "🔴" if "MALWARE" in threat else "🟡"
    message["text"] += f"{icon} **{threat}**: {count} events\n"

# Status Summary
status_counts = {}
for event in malicious:
    status = event.get('status', 'N/A')
    status_counts[status] = status_counts.get(status, 0) + 1

message["text"] += "\n### ✅ Status:\n\n"
for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
    icon = "🔴" if status == "OPEN" else "⚠️" if status == "REOPEN" else "✅"
    message["text"] += f"{icon} **{status}**: {count}\n"

# Top 5 Recent Events (เรียงตามเวลาไทย)
message["text"] += "\n### 📋 Recent Events (Top 5):\n\n"
recent_5 = sorted(
    [e for e in malicious if e.get('_bangkok_time')],
    key=lambda x: x['_bangkok_time'],
    reverse=True
)[:5]

for i, event in enumerate(recent_5, 1):
    event_id = event.get('id')
    dt_bangkok = event['_bangkok_time']
    threat = event.get('threat_type', 'N/A')
    action = event.get('action', 'N/A')
    status = event.get('status', 'N/A')
    path = event.get('path', 'N/A')
    
    # Shorten path
    if path and len(path) > 60:
        path = "..." + path[-57:]
    
    # แสดงเวลาไทย
    time_str = dt_bangkok.strftime('%H:%M:%S')
    
    message["text"] += f"{i}. **[{event_id}]** {time_str} - {threat}\n"
    message["text"] += f"   - Status: {status} | Action: {action}\n"
    message["text"] += f"   - Path: `{path}`\n\n"

# Footer
message["text"] += "---\n"
message["text"] += "*🔒 Powered by Deep Instinct API Integration*"

# 4. ส่งไปยัง Mattermost
print("📤 กำลังส่งไปยัง Mattermost...")
print()

try:
    webhook_response = requests.post(
        webhook_url,
        json=message,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    if webhook_response.status_code == 200:
        print("✅ ส่งข้อความไปยัง Mattermost สำเร็จ!")
        print()
        print("=" * 60)
        print("📝 Preview ข้อความที่ส่ง:")
        print("=" * 60)
        print(message["text"])
        print()
        print("=" * 60)
        print("🕐 เวลาที่แสดงเป็น: GMT+7 (เวลาไทย)")
        print("=" * 60)
    else:
        print(f"❌ Error: {webhook_response.status_code}")
        print(f"Response: {webhook_response.text}")
        
except Exception as e:
    print(f"❌ Error sending to Mattermost: {e}")
