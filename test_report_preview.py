#!/usr/bin/env python3
"""
Test Daily Report with Real Data - Preview Only (ไม่ส่ง Mattermost)
ดึงข้อมูลจริงจาก Deep Instinct API และแสดง preview รายงาน
"""

import os
import sys
import requests
from datetime import datetime, timezone, timedelta, date
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv('/home/api/deep-api/.env')

# Configuration
API_URL = os.getenv('DEEPINSTINCT_URL')
TOKEN = os.getenv('TOKENS_KEY')
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


def fetch_events_with_pagination(endpoint, after_id, max_pages=50):
    """ดึง events พร้อม pagination (เพิ่ม max_pages เป็น 50)"""
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
            
            if isinstance(data, dict):
                events_batch = data.get('events', [])
                last_id = data.get('last_id')
            elif isinstance(data, list):
                events_batch = data
                last_id = None
            else:
                break
            
            if not events_batch:
                break
            
            all_events.extend(events_batch)
            
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


def build_mattermost_message_preview(malicious_events, suspicious_events, report_date=None):
    """สร้างข้อความสำหรับ Mattermost แบบตาราง"""
    
    now_bangkok = datetime.now(TZ_BANGKOK)
    if report_date:
        if hasattr(report_date, 'strftime'):
            day = report_date.day
            month = report_date.month
            year = report_date.year + 543  # แปลง ค.ศ. เป็น พ.ศ.
            date_str = f"{day:02d}/{month:02d}/{year}"
            date_display = f"{day}/{month}/{year}"
        else:
            date_str = str(report_date)
            date_display = str(report_date)
    else:
        day = now_bangkok.day
        month = now_bangkok.month
        year = now_bangkok.year + 543
        date_str = f"{day:02d}/{month:02d}/{year}"
        date_display = f"{day}/{month}/{year}"
    
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
        
        if severity != 'N/A':
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    total_events = len(malicious_events) + len(suspicious_events)
    
    # สร้าง message
    message = f"""### 🔒 Deep Instinct Security Report

**วันที่:** {date_str} | **เวลา:** {time_str} (GMT+7)

---

#### 📊 สรุป Events วันที่ {date_display}

| หมวดหมู่ | จำนวน |
|:---------|------:|
| 🔴 Malicious | {len(malicious_events)} |
| 🟡 Suspicious | {len(suspicious_events)} |
| **รวมทั้งหมด** | **{total_events}** |

---

#### 🛡️ การดำเนินการ (Actions)

| Action | จำนวน |
|:-------|------:|
| 👁️ DETECTED | {detected_count} |
| 🛡️ PREVENTED | {prevented_count} |

---

#### ⚠️ ระดับความรุนแรง (Threat Severity)

"""
    
    # แสดง Severity ที่มีค่ามากกว่า 0
    severity_display = {
        'CRITICAL': '🔴 CRITICAL',
        'VERY_HIGH': '🔴 VERY_HIGH',
        'HIGH': '🟠 HIGH',
        'MODERATE': '🟡 MODERATE',
        'LOW': '🟢 LOW',
        'VERY_LOW': '⚪ VERY_LOW'
    }
    
    has_severity = False
    for severity in ['MODERATE', 'LOW', 'VERY_LOW', 'HIGH', 'VERY_HIGH', 'CRITICAL']:
        if severity in severity_counts and severity_counts[severity] > 0:
            if not has_severity:
                has_severity = True
            message += f"| {severity_display[severity]} | {severity_counts[severity]} |\n"
    
    if not has_severity:
        message += "| ไม่มีข้อมูล | 0 |\n"
    
    message += "\n---\n\n"
    
    # Link to report
    date_filename = (report_date or datetime.now(TZ_BANGKOK).date()).strftime('%Y-%m-%d')
    details_url = f"{REPORT_SERVER_URL.rstrip('/')}/event_detail/event_details_{date_filename}.html"
    message += f"📄 [ดูรายละเอียด Events ทั้งหมด]({details_url})\n\n"
    message += "🔗 [Deep Instinct Dashboard](https://ro.customers.deepinstinctweb.com)\n"
    
    return message


def main():
    """Main function - ดึงข้อมูลจริงแต่ไม่ส่ง Mattermost"""
    
    # รองรับการระบุวันที่
    target_date = None
    if len(sys.argv) >= 2:
        arg = sys.argv[1]
        if arg.lower() == 'yesterday':
            target_date = (date.today() - timedelta(days=1))
        elif '-' in arg:
            parts = arg.split('-')
            if len(parts) == 3:
                if len(parts[0]) == 4 and parts[0].isdigit():
                    target_date = datetime.strptime(arg, '%Y-%m-%d').date()
                elif len(parts[2]) == 2:  # 15-2-69 format
                    year_be = int(parts[2]) + 2500
                    year_ce = year_be - 543
                    target_date = date(year_ce, int(parts[1]), int(parts[0]))
                else:
                    target_date = datetime.strptime(arg, '%Y-%m-%d').date()
    
    if target_date:
        date_str = target_date.strftime('%Y-%m-%d')
        print("╔══════════════════════════════════════════════════════════════╗")
        print(f"║   Preview Report: {date_str} (ไม่ส่ง Mattermost)         ║")
        print("╚══════════════════════════════════════════════════════════════╝")
    else:
        target_date = (date.today() - timedelta(days=1))  # Default: เมื่อวาน
        date_str = target_date.strftime('%Y-%m-%d')
        print("╔══════════════════════════════════════════════════════════════╗")
        print(f"║   Preview Report: Yesterday ({date_str})                   ║")
        print("║   (ไม่ส่ง Mattermost - Preview Only)                       ║")
        print("╚══════════════════════════════════════════════════════════════╝")
    
    print()
    print(f"📅 Target Date: {date_str}")
    print()
    
    # 1. ดึง Malicious Events
    print("📥 Fetching Malicious Events...")
    try:
        malicious = fetch_events_with_pagination('events', 17400)
        malicious_filtered = filter_by_date(malicious, target_date)
        print(f"   ✅ Found {len(malicious_filtered)} malicious events")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        malicious_filtered = []
    
    # 2. ดึง Suspicious Events
    print("\n📥 Fetching Suspicious Events...")
    try:
        suspicious = fetch_events_with_pagination('suspicious-events', 14400)
        suspicious_filtered = filter_by_date(suspicious, target_date)
        print(f"   ✅ Found {len(suspicious_filtered)} suspicious events")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        suspicious_filtered = []
    
    # 3. สร้าง Preview Message
    print("\n" + "=" * 70)
    print("  📨 PREVIEW MESSAGE (จะแสดงใน Mattermost):")
    print("=" * 70)
    print()
    
    message = build_mattermost_message_preview(
        malicious_filtered,
        suspicious_filtered,
        target_date
    )
    
    print(message)
    
    print("=" * 70)
    print()
    
    # 4. สรุป
    total = len(malicious_filtered) + len(suspicious_filtered)
    print(f"📊 Summary:")
    print(f"   Malicious: {len(malicious_filtered)}")
    print(f"   Suspicious: {len(suspicious_filtered)}")
    print(f"   Total: {total}")
    print()
    
    if total == 0:
        print("ℹ️  ไม่มี events สำหรับวันที่นี้")
    else:
        print("✅ Preview สำเร็จ!")
    
    print()
    print("💡 หมายเหตุ:")
    print("   - นี่คือ PREVIEW เท่านั้น ยังไม่ได้ส่งไป Mattermost")
    print("   - ถ้าต้องการส่งจริง ใช้: python3 send_today_to_mattermost.py")
    print(f"   - รูปแบบตารางจะแสดงสวยงามใน Mattermost")
    print()


if __name__ == "__main__":
    print()
    print("🧪 Test Report Format with Real Data")
    print()
    print("Usage:")
    print("  python3 test_report_preview.py              # เมื่อวาน")
    print("  python3 test_report_preview.py yesterday    # เมื่อวาน")
    print("  python3 test_report_preview.py 2026-02-15   # วันที่กำหนด")
    print("  python3 test_report_preview.py 15-2-69      # วันที่กำหนด (พ.ศ.)")
    print()
    print("-" * 70)
    print()
    
    main()
