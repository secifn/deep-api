#!/usr/bin/env python3
"""
ดึง Events ทั้งหมดของวันนี้ (Malicious + Suspicious)
แยกตาม Action: DETECTED และ PREVENTED
"""

from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone, timedelta
import json

load_dotenv('.env1')

token = os.getenv('TOKENS_KEY')
base_url = os.getenv('DEEPINSTINCT_URL').rstrip('/')

# Timezone สำหรับประเทศไทย (GMT+7)
TZ_BANGKOK = timezone(timedelta(hours=7))

def convert_to_bangkok_time(iso_timestamp):
    """แปลง ISO timestamp เป็นเวลาไทย (GMT+7)"""
    if not iso_timestamp:
        return None
    dt_utc = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    return dt_utc.astimezone(TZ_BANGKOK)

def fetch_events_with_pagination(endpoint, after_id=17400, max_pages=20):
    """ดึง events แบบ pagination"""
    url = f"{base_url}{endpoint}"
    all_events = []
    current_after_id = after_id
    
    for page in range(max_pages):
        params = {"after_event_id": current_after_id}
        response = requests.get(url, headers={'Authorization': token}, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error {endpoint}: {response.status_code}")
            break
        
        result = response.json()
        if isinstance(result, dict):
            events_batch = result.get('events', [])
        else:
            events_batch = result
        
        if not events_batch:
            break
        
        all_events.extend(events_batch)
        
        # หา max event ID
        batch_max_id = current_after_id
        for event in events_batch:
            event_id = event.get('id')
            if event_id and event_id > batch_max_id:
                batch_max_id = event_id
        
        if batch_max_id == current_after_id or len(events_batch) < 50:
            break
        
        current_after_id = batch_max_id
    
    return all_events

def filter_today(events, today_str):
    """Filter events ของวันนี้"""
    today_events = []
    for event in events:
        ts = event.get('timestamp') or event.get('recorded_device_timestamp')
        if ts:
            try:
                dt_bangkok = convert_to_bangkok_time(ts)
                if dt_bangkok and dt_bangkok.strftime('%Y-%m-%d') == today_str:
                    event['_bangkok_time'] = dt_bangkok
                    today_events.append(event)
            except:
                pass
    return today_events

def print_header(title):
    """พิมพ์ header สวยๆ"""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_event_summary(events, event_type):
    """แสดงสรุป events"""
    if not events:
        print(f"  ไม่มี {event_type} events ในวันนี้")
        return
    
    # สถิติ
    action_counts = {}
    status_counts = {}
    threat_counts = {}
    severity_counts = {}
    
    for event in events:
        action = event.get('action', 'N/A')
        status = event.get('status', 'N/A')
        threat = event.get('threat_type', 'N/A')
        severity = event.get('threat_severity', 'N/A')
        
        action_counts[action] = action_counts.get(action, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
        threat_counts[threat] = threat_counts.get(threat, 0) + 1
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print(f"\n📊 {event_type} Events: {len(events)} รายการ\n")
    
    # Severity
    print("⚠️  Threat Severity:")
    severity_order = ['CRITICAL', 'VERY_HIGH', 'HIGH', 'MODERATE', 'LOW', 'VERY_LOW', 'N/A']
    for severity in severity_order:
        if severity in severity_counts:
            count = severity_counts[severity]
            if severity == 'CRITICAL':
                icon = "🔴"
            elif severity == 'VERY_HIGH':
                icon = "🔴"
            elif severity == 'HIGH':
                icon = "🟠"
            elif severity == 'MODERATE':
                icon = "🟡"
            elif severity == 'LOW':
                icon = "🟢"
            elif severity == 'VERY_LOW':
                icon = "⚪"
            else:
                icon = "❓"
            print(f"  {icon} {severity}: {count}")
    
    # Actions
    print("\n🛡️  Actions:")
    for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
        icon = "🛡️" if action == "PREVENTED" else "👁️" if action == "DETECTED" else "❓"
        print(f"  {icon} {action}: {count}")
    
    # Status
    print("\n✅ Status:")
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        icon = "🔴" if status == "OPEN" else "⚠️" if status == "REOPEN" else "✅"
        print(f"  {icon} {status}: {count}")
    
    # Top Threats
    print("\n🎯 Top 5 Threat Types:")
    for threat, count in sorted(threat_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        icon = "🔴" if "MALWARE" in threat else "🟡"
        print(f"  {icon} {threat}: {count}")

def print_recent_events(events, event_type, limit=10):
    """แสดง events ล่าสุด"""
    if not events:
        return
    
    print(f"\n📋 {event_type} Events ล่าสุด (Top {limit}):")
    print("-" * 70)
    
    recent = sorted(
        [e for e in events if e.get('_bangkok_time')],
        key=lambda x: x['_bangkok_time'],
        reverse=True
    )[:limit]
    
    for i, event in enumerate(recent, 1):
        event_id = event.get('id')
        dt = event.get('_bangkok_time')
        threat = event.get('threat_type', 'N/A')
        action = event.get('action', 'N/A')
        status = event.get('status', 'N/A')
        severity = event.get('threat_severity', 'N/A')
        path = event.get('path', 'N/A')
        
        time_str = dt.strftime('%H:%M:%S')
        status_icon = "🔴" if status == "OPEN" else "⚠️" if status == "REOPEN" else "✅"
        action_icon = "🛡️" if action == "PREVENTED" else "👁️"
        
        # Severity icon
        if severity == 'CRITICAL':
            severity_icon = "🔴"
        elif severity == 'VERY_HIGH':
            severity_icon = "🔴"
        elif severity == 'HIGH':
            severity_icon = "🟠"
        elif severity == 'MODERATE':
            severity_icon = "🟡"
        elif severity == 'LOW':
            severity_icon = "🟢"
        elif severity == 'VERY_LOW':
            severity_icon = "⚪"
        else:
            severity_icon = "❓"
        
        print(f"\n{i:2d}. {status_icon}{action_icon}{severity_icon} [{event_id}] {time_str} - {threat}")
        print(f"    Status: {status} | Action: {action} | Severity: {severity}")
        
        if path and path != 'N/A':
            if len(path) > 60:
                path = "..." + path[-57:]
            print(f"    📂 {path}")

def save_to_json(malicious, suspicious, filename):
    """บันทึก events เป็น JSON"""
    data = {
        'generated_at': datetime.now(TZ_BANGKOK).isoformat(),
        'summary': {
            'malicious_count': len(malicious),
            'suspicious_count': len(suspicious),
            'total_count': len(malicious) + len(suspicious)
        },
        'malicious_events': malicious,
        'suspicious_events': suspicious
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 บันทึกข้อมูลไปยัง: {filename}")

# ===== MAIN =====

print("╔══════════════════════════════════════════════════════════════╗")
print("║   📊 ดึง Events ทั้งหมดของวันนี้                           ║")
print("║   (Malicious + Suspicious)                                   ║")
print("╚══════════════════════════════════════════════════════════════╝")

now_bangkok = datetime.now(TZ_BANGKOK)
today_str = now_bangkok.strftime('%Y-%m-%d')

print(f"\n📅 วันที่: {now_bangkok.strftime('%Y-%m-%d %H:%M:%S')} (GMT+7)")

# ===== 1. ดึง Malicious Events =====
print_header("🔴 กำลังดึง Malicious Events...")

malicious_all = fetch_events_with_pagination('/events/')
print(f"  ดึงได้: {len(malicious_all)} events")

malicious_today = filter_today(malicious_all, today_str)
print(f"  ของวันนี้: {len(malicious_today)} events")

# ===== 2. ดึง Suspicious Events =====
print_header("🟡 กำลังดึง Suspicious Events...")

# Suspicious events ใช้ event ID คนละ range - ต้องเริ่มจาก ID ที่เล็กกว่า
suspicious_all = fetch_events_with_pagination('/suspicious-events/', after_id=14400, max_pages=20)
print(f"  ดึงได้: {len(suspicious_all)} events")

suspicious_today = filter_today(suspicious_all, today_str)
print(f"  ของวันนี้: {len(suspicious_today)} events")

# ===== 3. สรุปและแสดงผล =====
print_header("📊 สรุปผล")

total = len(malicious_today) + len(suspicious_today)
print(f"\n🎯 Total Events ของวันนี้: {total}")
print(f"  🔴 Malicious: {len(malicious_today)}")
print(f"  🟡 Suspicious: {len(suspicious_today)}")

# แยกตาม Action
all_events = malicious_today + suspicious_today

detected = [e for e in all_events if e.get('action') == 'DETECTED']
prevented = [e for e in all_events if e.get('action') == 'PREVENTED']
other = [e for e in all_events if e.get('action') not in ['DETECTED', 'PREVENTED']]

print(f"\n🛡️  แยกตาม Action:")
print(f"  👁️  DETECTED: {len(detected)}")
print(f"  🛡️  PREVENTED: {len(prevented)}")
if other:
    print(f"  ❓ Other: {len(other)}")

# ===== 4. แสดงรายละเอียด =====
print_header("🔴 MALICIOUS EVENTS")
print_event_summary(malicious_today, "Malicious")
print_recent_events(malicious_today, "Malicious", limit=10)

print_header("🟡 SUSPICIOUS EVENTS")
print_event_summary(suspicious_today, "Suspicious")
print_recent_events(suspicious_today, "Suspicious", limit=10)

# ===== 5. แยกตาม Action (รวม) =====
if detected:
    print_header("👁️  DETECTED Events (รวม Malicious + Suspicious)")
    print_recent_events(detected, "DETECTED", limit=10)

if prevented:
    print_header("🛡️  PREVENTED Events (รวม Malicious + Suspicious)")
    print_recent_events(prevented, "PREVENTED", limit=10)

# ===== 6. บันทึกเป็น JSON =====
print_header("💾 บันทึกข้อมูล")

filename = f"events_today_{today_str}.json"
save_to_json(malicious_today, suspicious_today, filename)

# ===== 7. สรุปท้าย =====
print()
print("=" * 70)
print("✅ เสร็จสิ้น!")
print("=" * 70)
print(f"\n📊 สรุป:")
print(f"  - Total Events: {total}")
print(f"  - Malicious: {len(malicious_today)}")
print(f"  - Suspicious: {len(suspicious_today)}")
print(f"  - Detected: {len(detected)}")
print(f"  - Prevented: {len(prevented)}")
print(f"  - Saved to: {filename}")
print()
