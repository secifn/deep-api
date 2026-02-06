#!/usr/bin/env python3
"""
Deep Instinct to Mattermost - Daily Report with Threat Severity
ส่งรายงาน Events ของวันนี้ไปยัง Mattermost พร้อม Threat Severity
"""

import os
import sys
import requests
import json
from datetime import datetime, timezone, timedelta, date
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv('/home/api/DeepInstint/.env1')

# Configuration
API_URL = os.getenv('DEEPINSTINCT_URL')
TOKEN = os.getenv('TOKENS_KEY')
WEBHOOK_URL = os.getenv('MATTERMOST_WEBHOOK_URL')
REPORT_SERVER_URL = os.getenv('REPORT_SERVER_URL', 'http://localhost:8080')

# Bangkok timezone
TZ_BANGKOK = timezone(timedelta(hours=7))

def convert_to_bangkok_time(iso_timestamp):
    """แปลง ISO timestamp เป็นเวลา Bangkok"""
    if not iso_timestamp:
        return None
    dt_utc = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    dt_bangkok = dt_utc.astimezone(TZ_BANGKOK)
    return dt_bangkok

def filter_today(events):
    """กรองเฉพาะ events ของวันนี้"""
    today_bangkok = datetime.now(TZ_BANGKOK).date()
    return filter_by_date(events, today_bangkok)

def filter_by_date(events, target_date):
    """กรองเฉพาะ events ของวันที่กำหนด"""
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    filtered = []
    for event in events:
        timestamp = event.get('timestamp') or event.get('insertion_timestamp')
        if timestamp:
            dt_bangkok = convert_to_bangkok_time(timestamp)
            if dt_bangkok and dt_bangkok.date() == target_date:
                event['_bangkok_time'] = dt_bangkok
                filtered.append(event)
    return filtered

def fetch_events_with_pagination(endpoint, after_id, max_pages=20):
    """ดึง events พร้อม pagination"""
    url = f"{API_URL}{endpoint}"
    headers = {'Authorization': TOKEN}
    
    all_events = []
    current_after_id = after_id
    
    for page in range(max_pages):
        params = {"after_event_id": current_after_id}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # API อาจกลับมาเป็น list หรือ dict
            if isinstance(data, dict):
                events_batch = data.get('events', [])
                last_id = data.get('last_id')
            elif isinstance(data, list):
                events_batch = data
                last_id = None
            else:
                print(f"⚠️  Unexpected response format: {type(data)}")
                break
            
            if not events_batch:
                break
            
            all_events.extend(events_batch)
            
            # ใช้ last_id จาก response หรือ max id จาก events
            if last_id:
                current_after_id = last_id
            else:
                max_id = max(e.get('id', 0) for e in events_batch)
                if max_id <= current_after_id:
                    break
                current_after_id = max_id
            
        except Exception as e:
            print(f"⚠️  Error fetching {endpoint} page {page+1}: {e}")
            break
    
    return all_events

def get_severity_icon(severity):
    """ดึง icon สำหรับ severity level"""
    severity_map = {
        'CRITICAL': '🔴',
        'VERY_HIGH': '🔴',
        'HIGH': '🟠',
        'MODERATE': '🟡',
        'LOW': '🟢',
        'VERY_LOW': '⚪',
    }
    return severity_map.get(severity, '❓')

def build_event_details_html(malicious_events, suspicious_events, output_file):
    """สร้างไฟล์ HTML รายละเอียด Events"""
    
    now_bangkok = datetime.now(TZ_BANGKOK)
    date_str = now_bangkok.strftime('%d/%m/%Y %H:%M:%S')
    
    all_events = malicious_events + suspicious_events
    all_events_sorted = sorted(
        [e for e in all_events if e.get('_bangkok_time')],
        key=lambda x: x['_bangkok_time'],
        reverse=True
    )
    
    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>รายละเอียด Events - Deep Instinct</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .event-card {{ background: #f9f9f9; border-left: 4px solid #667eea; padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
        .event-card.malicious {{ border-left-color: #e74c3c; }}
        .event-card.suspicious {{ border-left-color: #f39c12; }}
        .event-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #e0e0e0; }}
        .event-id {{ font-size: 20px; font-weight: bold; color: #333; }}
        .event-time {{ color: #666; font-size: 14px; }}
        .section {{ margin-bottom: 20px; }}
        .section-title {{ font-size: 16px; font-weight: bold; color: #667eea; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 1px solid #e0e0e0; }}
        .detail-row {{ display: grid; grid-template-columns: 200px 1fr; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }}
        .detail-label {{ font-weight: 600; color: #555; }}
        .detail-value {{ color: #333; word-break: break-all; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-right: 5px; }}
        .badge.prevented {{ background: #e74c3c; color: white; }}
        .badge.detected {{ background: #3498db; color: white; }}
        .badge.severity-critical {{ background: #c0392b; color: white; }}
        .badge.severity-very-high {{ background: #e74c3c; color: white; }}
        .badge.severity-high {{ background: #e67e22; color: white; }}
        .badge.severity-moderate {{ background: #f39c12; color: white; }}
        .badge.severity-low {{ background: #27ae60; color: white; }}
        .badge.severity-very-low {{ background: #95a5a6; color: white; }}
        .hash {{ font-family: 'Courier New', monospace; font-size: 12px; background: #ecf0f1; padding: 5px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 รายละเอียด Security Events</h1>
            <p>สร้างเมื่อ: {date_str} (GMT+7)</p>
            <p>จำนวนทั้งหมด: {len(all_events_sorted)} events</p>
        </div>
        <div class="content">
"""
    
    for event in all_events_sorted:
        event_type = "malicious" if event in malicious_events else "suspicious"
        event_id = event.get('id', 'N/A')
        dt = event.get('_bangkok_time')
        time_str = dt.strftime('%d/%m/%Y %H:%M:%S') if dt else 'N/A'
        
        action = event.get('action', 'N/A')
        severity = event.get('threat_severity', 'N/A')
        threat_type = event.get('threat_type', 'N/A')
        description = event.get('description', 'N/A')
        
        # Device & User Details
        recorded_info = event.get('recorded_device_info', {})
        hostname = recorded_info.get('hostname', 'N/A')
        ip_address = recorded_info.get('ip_address', 'N/A')
        msp_name = event.get('msp_name', 'N/A')
        tenant_name = event.get('tenant_name', 'N/A')
        
        # Event Indicators
        filename = event.get('path', 'N/A')
        file_hash = event.get('file_hash', event.get('container_hash', 'N/A'))
        
        # Badges
        action_badge = f'<span class="badge {action.lower()}">{action}</span>'
        severity_class = severity.lower().replace('_', '-')
        severity_badge = f'<span class="badge severity-{severity_class}">{severity}</span>'
        
        html += f"""
            <div class="event-card {event_type}">
                <div class="event-header">
                    <div class="event-id">Event ID: {event_id}</div>
                    <div class="event-time">{time_str}</div>
                </div>
                
                <div style="margin-bottom: 15px;">
                    {action_badge}
                    {severity_badge}
                </div>
                
                <div class="section">
                    <div class="section-title">📋 ข้อมูลทั่วไป</div>
                    <div class="detail-row">
                        <div class="detail-label">Threat Type:</div>
                        <div class="detail-value">{threat_type}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Details:</div>
                        <div class="detail-value">{description}</div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">💻 Device & User Details</div>
                    <div class="detail-row">
                        <div class="detail-label">Device Name:</div>
                        <div class="detail-value">{hostname}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">IP Address:</div>
                        <div class="detail-value">{ip_address}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">MSP:</div>
                        <div class="detail-value">{msp_name}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Tenant:</div>
                        <div class="detail-value">{tenant_name}</div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">🔍 Event Indicators</div>
                    <div class="detail-row">
                        <div class="detail-label">Filename:</div>
                        <div class="detail-value">{filename}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">File Hash:</div>
                        <div class="detail-value"><span class="hash">{file_hash}</span></div>
                    </div>
                </div>
            </div>
"""
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    # บันทึกไฟล์
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_file

def build_mattermost_message(malicious_events, suspicious_events, details_url=None, report_date=None):
    """สร้างข้อความสำหรับ Mattermost พร้อม Threat Severity"""
    
    now_bangkok = datetime.now(TZ_BANGKOK)
    if report_date:
        date_str = report_date.strftime('%d/%m/%Y') if hasattr(report_date, 'strftime') else str(report_date)
    else:
        date_str = now_bangkok.strftime('%d/%m/%Y')
    time_str = now_bangkok.strftime('%H:%M:%S')
    
    # นับ Actions
    detected_count = 0
    prevented_count = 0
    
    # นับ Severity
    severity_counts = {}
    
    for event in malicious_events + suspicious_events:
        action = event.get('action', 'N/A')
        severity = event.get('threat_severity', 'N/A')
        
        if action == 'DETECTED':
            detected_count += 1
        elif action == 'PREVENTED':
            prevented_count += 1
        
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    total_events = len(malicious_events) + len(suspicious_events)
    
    # สร้าง Markdown message
    message = f"""
### 🔒 Deep Instinct Security Report
**วันที่:** {date_str} | **เวลา:** {time_str} (GMT+7)

---

#### 📊 สรุป Events วันที่ {date_str}

| หมวดหมู่ | จำนวน |
|:---------|------:|
| 🔴 **Malicious** | **{len(malicious_events)}** |
| 🟡 **Suspicious** | **{len(suspicious_events)}** |
| **รวมทั้งหมด** | **{total_events}** |

---

#### 🛡️ การดำเนินการ (Actions)

| Action | จำนวน |
|:-------|------:|
| 👁️ **DETECTED** | **{detected_count}** |
| 🛡️ **PREVENTED** | **{prevented_count}** |

---

#### ⚠️ ระดับความรุนแรง (Threat Severity)

"""
    
    # แสดง Severity แบบเรียง
    severity_order = ['CRITICAL', 'VERY_HIGH', 'HIGH', 'MODERATE', 'LOW', 'VERY_LOW', 'N/A']
    for severity in severity_order:
        if severity in severity_counts:
            count = severity_counts[severity]
            icon = get_severity_icon(severity)
            message += f"| {icon} **{severity}** | **{count}** |\n"
    
    message += "\n---\n\n"
    
    # เพิ่ม link ไปยังรายละเอียด
    if details_url:
        message += f"📄 [ดูรายละเอียด Events ทั้งหมด]({details_url})\n\n"
    
    message += "🔗 [Deep Instinct Dashboard](https://ro.customers.deepinstinctweb.com)\n"
    
    return message

def send_to_mattermost(message):
    """ส่งข้อความไปยัง Mattermost"""
    payload = {
        "text": message,
        "username": "Deep Instinct Security Bot",
        "icon_emoji": ":shield:"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Error sending to Mattermost: {e}")
        return False

def main():
    """Main function"""
    # รองรับการระบุวันที่: python script.py 2026-02-04 หรือ 4-2-69 (วัน-เดือน-พ.ศ.)
    target_date = None
    if len(sys.argv) >= 2:
        arg = sys.argv[1]
        if '-' in arg:
            parts = arg.split('-')
            if len(parts) == 3:
                # YYYY-MM-DD (ปี 4 หลักอยู่หน้า)
                if len(parts[0]) == 4 and parts[0].isdigit():
                    target_date = datetime.strptime(arg, '%Y-%m-%d').date()
                elif len(parts[2]) == 2:  # 4-2-69 format (วัน-เดือน-พ.ศ. 2 หลัก)
                    year_be = int(parts[2]) + 2500  # 69 -> 2569
                    year_ce = year_be - 543  # แปลง พ.ศ. -> ค.ศ.
                    target_date = date(year_ce, int(parts[1]), int(parts[0]))
                else:
                    target_date = datetime.strptime(arg, '%Y-%m-%d').date()
    
    if target_date:
        date_str = target_date.strftime('%Y-%m-%d')
        print("=" * 70)
        print(f"  🔒 Deep Instinct → Mattermost (Report วันที่ {date_str})")
        print("=" * 70)
    else:
        print("=" * 70)
        print("  🔒 Deep Instinct → Mattermost (Daily Report)")
        print("=" * 70)
    
    # 1. ดึง Malicious Events
    print("\n📥 Fetching Malicious Events...")
    malicious = fetch_events_with_pagination('events', 17400)
    malicious_filtered = filter_by_date(malicious, target_date or datetime.now(TZ_BANGKOK).date())
    print(f"   ✅ Found {len(malicious_filtered)} malicious events")
    
    # 2. ดึง Suspicious Events
    print("\n📥 Fetching Suspicious Events...")
    suspicious = fetch_events_with_pagination('suspicious-events', 14400)
    suspicious_filtered = filter_by_date(suspicious, target_date or datetime.now(TZ_BANGKOK).date())
    print(f"   ✅ Found {len(suspicious_filtered)} suspicious events")
    
    # 3. สร้างไฟล์ HTML รายละเอียด
    print("\n📄 Creating detailed HTML report...")
    date_filename = (target_date or datetime.now(TZ_BANGKOK).date()).strftime('%Y-%m-%d')
    html_filename = f"event_details_{date_filename}.html"
    html_path = f"/home/api/DeepInstint/{html_filename}"
    
    build_event_details_html(malicious_filtered, suspicious_filtered, html_path)
    print(f"   ✅ Created: {html_filename}")
    
    # URL สำหรับเข้าถึงไฟล์ผ่าน web server
    details_url = f"{REPORT_SERVER_URL}/{html_filename}"
    print(f"   🔗 Report URL: {details_url}")
    
    # 4. สร้างข้อความ Mattermost
    print("\n📝 Building Mattermost message...")
    report_date = target_date or datetime.now(TZ_BANGKOK).date()
    message = build_mattermost_message(malicious_filtered, suspicious_filtered, details_url, report_date)
    
    # 5. แสดงตัวอย่าง
    print("\n" + "=" * 70)
    print("  📨 Preview Message:")
    print("=" * 70)
    print(message)
    print("=" * 70)
    
    # 6. ส่งไปยัง Mattermost
    print("\n📤 Sending to Mattermost...")
    success = send_to_mattermost(message)
    
    if success:
        print("   ✅ Sent successfully!")
        print(f"\n📄 Detailed report: {html_path}")
    else:
        print("   ❌ Failed to send")
    
    print("\n" + "=" * 70)
    print("  ✅ Done!")
    print("=" * 70)

if __name__ == "__main__":
    main()
