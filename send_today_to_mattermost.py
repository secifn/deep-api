#!/usr/bin/env python3
"""
Deep Instinct to Mattermost - Daily Report with Threat Severity
ส่งรายงาน Events ของวันนี้ไปยัง Mattermost พร้อม Threat Severity
พร้อมบันทึก events ลง SQLite database
"""

import os
import sys
import requests
import json
from datetime import datetime, timezone, timedelta, date
from dotenv import load_dotenv
from database import get_db
from build_not_found_devices_html import build_not_found_devices_html
from build_royal_devices_html import build_royal_devices_html
from build_reports_index import build_reports_index

# โหลด environment variables
# โหลดจาก .env ในโฟลเดอร์โปรเจกต์ (Docker ใช้ env_file จาก docker-compose)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, '.env'), override=True)  # override เพื่อใช้ค่าจาก .env ล่าสุด (รองรับการเปลี่ยน webhook)

# Configuration
API_URL = os.getenv('DEEPINSTINCT_URL')
TOKEN = os.getenv('TOKENS_KEY')
WEBHOOK_URL = os.getenv('MATTERMOST_WEBHOOK_URL')
REPORT_SERVER_URL = os.getenv('REPORT_SERVER_URL', 'http://localhost:8080')
IT_PARCEL_API_URL = os.getenv('IT_PARCEL_API_URL', '').rstrip('/')
IT_PARCEL_TOKEN = os.getenv('IT_PARCEL_TOKEN', '')

# Bangkok timezone
TZ_BANGKOK = timezone(timedelta(hours=7))

# โฟลเดอร์เก็บไฟล์ HTML รายละเอียด Events แต่ละวัน
EVENT_DETAIL_DIR = os.path.join(SCRIPT_DIR, 'event_detail')


def get_snipit_responsible_lookup(extra_search_hostnames=None):
    """
    ดึงรายการ Hardware จาก Snip IT (IT Parcel) แล้วสร้าง dict ชื่อเครื่อง -> ผู้รับผิดชอบ
    ใช้จับคู่กับ Deep Instinct event ตาม hostname/ชื่อเครื่อง
    ถ้า extra_search_hostnames ให้ จะใช้ Search API สำหรับ hostname ที่ยังไม่พบ (รองรับ custom field เช่น Device Name)
    คืนค่า dict (อาจว่างถ้าไม่มี config หรือ API ล้มเหลว)
    """
    if not IT_PARCEL_API_URL or not IT_PARCEL_TOKEN:
        return {}
    url = f"{IT_PARCEL_API_URL}/hardware"
    headers = {"Authorization": f"Bearer {IT_PARCEL_TOKEN}", "Accept": "application/json"}
    rows = []
    offset = 0
    limit = 200
    try:
        while True:
            params = {"limit": limit, "offset": offset}
            r = requests.get(url, headers=headers, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            page = data.get("rows") or data.get("data") or (data if isinstance(data, list) else [])
            if not page:
                break
            rows.extend(page)
            total = data.get("total") if isinstance(data, dict) else None
            if total is not None and offset + len(page) >= total:
                break
            if len(page) < limit:
                break
            offset += limit
    except Exception:
        pass
    def _row_to_info(row):
        assigned = row.get("assigned_to")
        if isinstance(assigned, dict):
            responsible = (
                assigned.get("name")
                or assigned.get("username")
                or assigned.get("display_name")
                or str(assigned.get("id", ""))
            )
        else:
            responsible = str(assigned) if assigned else "-"
        cf = row.get("custom_fields") or {}
        dept = division = "N/A"
        if isinstance(cf, dict):
            fd = cf.get("แผนก")
            if isinstance(fd, dict) and fd.get("value"):
                dept = fd.get("value")
            fk = cf.get("กอง")
            if isinstance(fk, dict) and fk.get("value"):
                division = fk.get("value")
        return {"responsible": responsible, "แผนก": dept, "กอง": division}

    lookup = {}
    for row in rows:
        name = row.get("name") or row.get("asset_tag") or row.get("hostname") or row.get("device_name") or ""
        asset_tag = row.get("asset_tag") or ""
        hostname = row.get("hostname") or ""
        serial = row.get("serial") or ""
        info = _row_to_info(row)
        keys_to_add = [name, asset_tag, hostname, serial]
        custom_fields = row.get("custom_fields") or {}
        if isinstance(custom_fields, dict):
            for field_name, field_data in custom_fields.items():
                if isinstance(field_data, dict) and field_data.get("value"):
                    keys_to_add.append(field_data.get("value"))
                elif isinstance(field_data, (str, int, float)):
                    keys_to_add.append(field_data)
        for raw_key in keys_to_add:
            if raw_key is not None and str(raw_key).strip():
                key = str(raw_key).strip().lower()
                lookup[key] = info
    # สำหรับ hostname ที่ยังไม่พบ: ใช้ Search API
    if extra_search_hostnames:
        seen = set()
        for hostname in extra_search_hostnames:
            if not hostname or str(hostname).strip() in ("", "n/a"):
                continue
            key = str(hostname).strip().lower()
            if key in seen or lookup.get(key):
                continue
            seen.add(key)
            try:
                r = requests.get(url, headers=headers, params={"search": hostname.strip(), "limit": 5}, timeout=10)
                r.raise_for_status()
                data = r.json()
                search_rows = data.get("rows") or data.get("data") or []
                if len(search_rows) == 1:
                    lookup[key] = _row_to_info(search_rows[0])
            except Exception:
                pass
    return lookup

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
    """สร้างไฟล์ HTML รายละเอียด Events (จับคู่ Snip IT แสดงผู้รับผิดชอบเครื่อง)"""
    
    now_bangkok = datetime.now(TZ_BANGKOK)
    date_str = now_bangkok.strftime('%d/%m/%Y %H:%M:%S')
    
    all_events = malicious_events + suspicious_events
    # รวบรวม hostname ทั้งหมดจาก events เพื่อใช้ Search API สำหรับเครื่องที่ list ไม่มี (เช่น custom field Device Name)
    unique_hostnames = []
    seen_hn = set()
    for event in all_events:
        recorded_info = event.get("recorded_device_info") or {}
        hn = recorded_info.get("hostname")
        if hn and str(hn).strip() and str(hn).strip().lower() not in seen_hn:
            seen_hn.add(str(hn).strip().lower())
            unique_hostnames.append(hn)
    # ดึง mapping ชื่อเครื่อง -> ผู้รับผิดชอบ จาก Snip IT (list + search สำหรับ hostname ที่มีในรายงาน)
    snipit_lookup = get_snipit_responsible_lookup(extra_search_hostnames=unique_hostnames)
    
    # ตรวจสอบเครื่องที่ไม่พบใน Snip IT
    devices_not_found = []
    for event in all_events:
        recorded_info = event.get("recorded_device_info") or {}
        hostname = recorded_info.get("hostname")
        if hostname and str(hostname).strip() and str(hostname) != 'N/A':
            key = str(hostname).strip().lower()
            if key not in snipit_lookup:
                # เก็บข้อมูลเครื่องที่ไม่พบ
                device_info = {
                    'hostname': hostname,
                    'ip_address': recorded_info.get('ip_address', 'N/A'),
                    'os': recorded_info.get('os', 'N/A'),
                    'event_id': event.get('id'),
                    'event_type': 'malicious' if event in malicious_events else 'suspicious',
                    'timestamp': event.get('_bangkok_time')
                }
                # เช็คว่ามีในรายการแล้วหรือยัง (ตาม hostname)
                if not any(d['hostname'] == hostname for d in devices_not_found):
                    devices_not_found.append(device_info)
    
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
        # จับคู่กับ Snip IT (ผู้รับผิดชอบ, แผนก, กอง)
        if hostname and str(hostname) != 'N/A':
            info = snipit_lookup.get(str(hostname).strip().lower())
            if isinstance(info, dict):
                responsible = info.get("responsible", "N/A")
                snipit_dept = info.get("แผนก", "N/A")
                snipit_division = info.get("กอง", "N/A")
            else:
                responsible = info if info else "N/A"
                snipit_dept = snipit_division = "N/A"
        else:
            responsible = snipit_dept = snipit_division = 'N/A'
        # แสดงข้อความเมื่อไม่พบข้อมูลใน Snip IT (แทน N/A)
        _na_msg = "ไม่พบข้อมูลใน Snip IT"
        responsible_display = _na_msg if (not responsible or str(responsible).strip() in ("", "N/A", "-")) else responsible
        snipit_dept_display = _na_msg if (not snipit_dept or str(snipit_dept).strip() in ("", "N/A", "-")) else snipit_dept
        snipit_division_display = _na_msg if (not snipit_division or str(snipit_division).strip() in ("", "N/A", "-")) else snipit_division
        
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
                    <div class="detail-row">
                        <div class="detail-label">ผู้รับผิดชอบ (Snip IT):</div>
                        <div class="detail-value">{responsible_display}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">แผนก (Snip IT):</div>
                        <div class="detail-value">{snipit_dept_display}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">กอง (Snip IT):</div>
                        <div class="detail-value">{snipit_division_display}</div>
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
    
    return output_file, devices_not_found


def collect_royal_devices_with_events(malicious_events, suspicious_events):
    """
    รวบรวมเครื่องของ Royal Chitralada Projects แยกตาม Action
    Returns: (royal_detected, royal_prevented)
    royal_detected = [(device_name, [events]), ...]
    royal_prevented = [(device_name, [events]), ...]
    """
    from collections import defaultdict
    royal_detected = defaultdict(list)
    royal_prevented = defaultdict(list)

    def process_events(events, event_type):
        for event in events:
            tenant = event.get('tenant_name', '')
            if 'Royal Chitralada Projects' not in tenant:
                continue
            action = event.get('action', 'N/A')
            rec = event.get('recorded_device_info', {})
            device = rec.get('hostname') or rec.get('device_name') or event.get('device_name')
            if not device or device == 'N/A':
                continue
            e_copy = dict(event)
            e_copy['_event_type'] = event_type
            if action == 'DETECTED':
                royal_detected[device].append(e_copy)
            elif action == 'PREVENTED':
                royal_prevented[device].append(e_copy)

    process_events(malicious_events, 'malicious')
    process_events(suspicious_events, 'suspicious')

    return (
        list(royal_detected.items()),
        list(royal_prevented.items())
    )


def build_mattermost_message(malicious_events, suspicious_events, details_url=None, report_date=None, not_found_url=None, not_found_count=0, royal_detected_url=None, royal_prevented_url=None, reports_index_url=None):
    """สร้างข้อความสำหรับ Mattermost แบบตาราง (เหมือนในรูป)"""
    
    now_bangkok = datetime.now(TZ_BANGKOK)
    if report_date:
        # แปลงเป็น พ.ศ.
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
    
    # นับ unique devices แยกตาม action
    detected_devices = set()
    prevented_devices = set()
    
    # นับ unique devices จาก Royal Chitralada Projects แยกตาม action และประเภท event
    royal_detected_devices_malicious = set()
    royal_detected_devices_suspicious = set()
    royal_prevented_devices_malicious = set()
    royal_prevented_devices_suspicious = set()
    
    # นับ Severity
    severity_counts = {
        'CRITICAL': 0,
        'VERY_HIGH': 0,
        'HIGH': 0,
        'MODERATE': 0,
        'LOW': 0,
        'VERY_LOW': 0
    }
    
    # นับ events จาก Royal Chitralada Projects
    royal_malicious = 0
    royal_suspicious = 0
    
    # ประมวลผล Malicious Events
    for event in malicious_events:
        action = event.get('action', 'N/A')
        severity = event.get('threat_severity', 'N/A')
        tenant = event.get('tenant_name', '')
        
        # ดึงชื่อ device (hostname, device_name จาก recorded_info หรือ event level) + normalize ด้วย strip
        recorded_info = event.get('recorded_device_info', {})
        raw = recorded_info.get('hostname') or recorded_info.get('device_name') or event.get('device_name') or ''
        device_name = str(raw).strip() if raw and str(raw).lower() not in ('n/a', 'none', '') else None
        
        # ตรวจสอบว่าเป็น Royal Chitralada Projects หรือไม่
        is_royal = 'Royal Chitralada Projects' in tenant
        
        if action == 'DETECTED':
            detected_count += 1
            if device_name:
                detected_devices.add(device_name)
                if is_royal:
                    royal_detected_devices_malicious.add(device_name)
        elif action == 'PREVENTED':
            prevented_count += 1
            if device_name:
                prevented_devices.add(device_name)
                if is_royal:
                    royal_prevented_devices_malicious.add(device_name)
        
        if severity in severity_counts:
            severity_counts[severity] += 1
        
        if is_royal:
            royal_malicious += 1
    
    # ประมวลผล Suspicious Events
    for event in suspicious_events:
        action = event.get('action', 'N/A')
        severity = event.get('threat_severity', 'N/A')
        tenant = event.get('tenant_name', '')
        
        # ดึงชื่อ device (hostname, device_name จาก recorded_info หรือ event level) + normalize ด้วย strip
        recorded_info = event.get('recorded_device_info', {})
        raw = recorded_info.get('hostname') or recorded_info.get('device_name') or event.get('device_name') or ''
        device_name = str(raw).strip() if raw and str(raw).lower() not in ('n/a', 'none', '') else None
        
        # ตรวจสอบว่าเป็น Royal Chitralada Projects หรือไม่
        is_royal = 'Royal Chitralada Projects' in tenant
        
        if action == 'DETECTED':
            detected_count += 1
            if device_name:
                detected_devices.add(device_name)
                if is_royal:
                    royal_detected_devices_suspicious.add(device_name)
        elif action == 'PREVENTED':
            prevented_count += 1
            if device_name:
                prevented_devices.add(device_name)
                if is_royal:
                    royal_prevented_devices_suspicious.add(device_name)
        
        if severity in severity_counts:
            severity_counts[severity] += 1
        
        if is_royal:
            royal_suspicious += 1
    
    total_events = len(malicious_events) + len(suspicious_events)
    royal_total = royal_malicious + royal_suspicious
    
    # จำนวนเครื่องแยกตาม action
    detected_device_count = len(detected_devices)
    prevented_device_count = len(prevented_devices)
    
    # รวมจำนวนเครื่องจาก Royal Chitralada Projects (Malicious + Suspicious) แยกตาม action
    royal_detected_device_count = len(royal_detected_devices_malicious | royal_detected_devices_suspicious)
    royal_prevented_device_count = len(royal_prevented_devices_malicious | royal_prevented_devices_suspicious)

    # สร้างลิงก์สำหรับเลข Royal (คลิก DETECTED → หน้า DETECTED เท่านั้น, PREVENTED → หน้า PREVENTED เท่านั้น)
    if royal_detected_url and royal_detected_device_count > 0:
        royal_detected_display = f"[{royal_detected_device_count}]({royal_detected_url})"
    else:
        royal_detected_display = str(royal_detected_device_count)
    if royal_prevented_url and royal_prevented_device_count > 0:
        royal_prevented_display = f"[{royal_prevented_device_count}]({royal_prevented_url})"
    else:
        royal_prevented_display = str(royal_prevented_device_count)

    # สร้าง message แบบตาราง (เหมือนในรูป)
    message = f"""### 🔒 Deep Instinct Security Report

รายงานเหตุการณ์วันที่: {date_str} | ส่งเมื่อ: {time_str} (GMT+7)

---

#### 📊 สรุป Events วันที่ {date_display}

| หมวดหมู่ | จำนวน/เหตุการณ์ | เป็นเหตุการณ์ของโครงการส่วนพระองค์ |
|:---------|---------------:|----------------------------------:|
| 🔴 Malicious | {len(malicious_events)} | {royal_malicious} |
| 🟡 Suspicious | {len(suspicious_events)} | {royal_suspicious} |
| **รวมทั้งหมด** | **{total_events}** | **{royal_total}** |

---

#### 🛡️ การดำเนินการ (Actions)

| Action | จำนวน/เหตุการณ์ | จำนวน/เครื่อง | เป็นเครื่องของโครงการส่วนพระองค์/จำนวน |
|:-------|---------------:|-------------:|--------------------------------------:|
| 👁️ DETECTED | {detected_count} | {detected_device_count} | {royal_detected_display} |
| 🛡️ PREVENTED | {prevented_count} | {prevented_device_count} | {royal_prevented_display} |

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
        if severity_counts[severity] > 0:
            if not has_severity:
                has_severity = True
            message += f"| {severity_display[severity]} | {severity_counts[severity]} |\n"
    
    if not has_severity:
        message += "| ไม่มีข้อมูล | 0 |\n"
    
    message += "\n---\n\n"
    
    # แสดงข้อมูลเครื่องที่ไม่พบใน Snip IT (ก่อนลิงก์)
    if not_found_count > 0:
        message += f"⚠️ **พบ {not_found_count} เครื่องที่ไม่อยู่ใน Snip IT**\n\n"
    
    # เพิ่ม link ไปยังรายละเอียด
    if details_url:
        message += f"📄 [ดูรายละเอียด Events ทั้งหมด]({details_url})\n"
        
        # เพิ่มลิงก์สำหรับเครื่องที่ไม่พบใน Snip IT
        if not_found_url and not_found_count > 0:
            message += f"⚠️ [รายละเอียดเครื่องที่ไม่พบใน Snip IT ({not_found_count} เครื่อง)]({not_found_url})\n"
        
        # ลิงก์ไปยังหน้ารวมรายงาน (Daily-report, เครื่องที่ไม่อยู่ใน Snipe-IT) เพื่อดูย้อนหลัง
        if reports_index_url:
            message += f"🔗 [Deep Instinct Security Report]({reports_index_url})\n"
        
        message += "\n"
    
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
    # Initialize database
    db = get_db()
    
    # รองรับการระบุวันที่: python script.py 2026-02-04 หรือ 4-2-69 หรือ yesterday
    # ถ้าไม่ระบุ = ใช้เมื่อวาน (สำหรับ cron รายวัน)
    target_date = datetime.now(TZ_BANGKOK).date() - timedelta(days=1)  # default: เมื่อวาน
    if len(sys.argv) >= 2:
        arg = sys.argv[1]
        if arg.lower() == 'yesterday':
            target_date = datetime.now(TZ_BANGKOK).date() - timedelta(days=1)
        elif '-' in arg:
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
    
    # 1. ดึง Malicious Events (เริ่มจาก ID ย้อนหลัง 2-3 วัน เพื่อความเร็ว)
    print("\n📥 Fetching Malicious Events...")
    malicious = fetch_events_with_pagination('events', 19200)
    malicious_filtered = filter_by_date(malicious, target_date or datetime.now(TZ_BANGKOK).date())
    print(f"   ✅ Found {len(malicious_filtered)} malicious events")
    
    # 2. ดึง Suspicious Events (เริ่มจาก ID ย้อนหลัง 2-3 วัน)
    print("\n📥 Fetching Suspicious Events...")
    suspicious = fetch_events_with_pagination('suspicious-events', 14400)
    suspicious_filtered = filter_by_date(suspicious, target_date or datetime.now(TZ_BANGKOK).date())
    print(f"   ✅ Found {len(suspicious_filtered)} suspicious events")
    
    # 3. บันทึก events ลง database
    print("\n💾 Saving events to database...")
    
    # ดึง Snip IT lookup สำหรับบันทึกลง database
    all_events = malicious_filtered + suspicious_filtered
    unique_hostnames = []
    seen_hn = set()
    for event in all_events:
        recorded_info = event.get("recorded_device_info") or {}
        hn = recorded_info.get("hostname")
        if hn and str(hn).strip() and str(hn).strip().lower() not in seen_hn:
            seen_hn.add(str(hn).strip().lower())
            unique_hostnames.append(hn)
    
    snipit_lookup = get_snipit_responsible_lookup(extra_search_hostnames=unique_hostnames)
    
    # บันทึก malicious events
    mal_saved, mal_skipped = db.save_events_batch(malicious_filtered, 'malicious', snipit_lookup)
    print(f"   ✅ Malicious: {mal_saved} saved, {mal_skipped} skipped (duplicates)")
    
    # บันทึก suspicious events
    sus_saved, sus_skipped = db.save_events_batch(suspicious_filtered, 'suspicious', snipit_lookup)
    print(f"   ✅ Suspicious: {sus_saved} saved, {sus_skipped} skipped (duplicates)")
    
    # 4. สร้างไฟล์ HTML รายละเอียด (จับคู่ Snip IT แสดงผู้รับผิดชอบ) เก็บใน event_detail/
    print("\n📄 Creating detailed HTML report...")
    os.makedirs(EVENT_DETAIL_DIR, exist_ok=True)
    date_filename = (target_date or datetime.now(TZ_BANGKOK).date()).strftime('%Y-%m-%d')
    html_filename = f"event_details_{date_filename}.html"
    html_path = os.path.join(EVENT_DETAIL_DIR, html_filename)
    
    html_path, devices_not_found = build_event_details_html(malicious_filtered, suspicious_filtered, html_path)
    print(f"   ✅ Created: event_detail/{html_filename}")
    if IT_PARCEL_API_URL and IT_PARCEL_TOKEN:
        print(f"   📌 จับคู่ผู้รับผิดชอบจาก Snip IT (IT Parcel) แล้ว")
    
    # สร้างรายงานเครื่องที่ไม่พบใน Snip IT
    not_found_html_filename = f"not_found_devices_{date_filename}.html"
    not_found_html_path = os.path.join(EVENT_DETAIL_DIR, not_found_html_filename)
    not_found_url = f"{REPORT_SERVER_URL.rstrip('/')}/event_detail/{not_found_html_filename}"
    
    if devices_not_found:
        build_not_found_devices_html(devices_not_found, not_found_html_path)
        print(f"   ⚠️  พบ {len(devices_not_found)} เครื่องที่ไม่อยู่ใน Snip IT")
        print(f"   📄 Not Found Report: event_detail/{not_found_html_filename}")
    else:
        not_found_url = None
        print(f"   ✅ เครื่องทั้งหมดพบใน Snip IT")
    
    # URL สำหรับเข้าถึงไฟล์ผ่าน web server (อยู่ใน event_detail/)
    details_url = f"{REPORT_SERVER_URL.rstrip('/')}/event_detail/{html_filename}"
    print(f"   🔗 Report URL: {details_url}")

    # สร้างไฟล์ HTML เครื่องโครงการส่วนพระองค์ แยก DETECTED และ PREVENTED
    royal_detected_list, royal_prevented_list = collect_royal_devices_with_events(malicious_filtered, suspicious_filtered)
    royal_detected_filename, royal_prevented_filename = build_royal_devices_html(
        royal_detected_list, royal_prevented_list, EVENT_DETAIL_DIR, date_filename,
        target_date or datetime.now(TZ_BANGKOK).date()
    )
    base_url = REPORT_SERVER_URL.rstrip('/') + '/event_detail/'
    royal_detected_url = base_url + royal_detected_filename
    royal_prevented_url = base_url + royal_prevented_filename
    if royal_detected_list or royal_prevented_list:
        print(f"   👑 Royal DETECTED: event_detail/{royal_detected_filename}")
        print(f"   👑 Royal PREVENTED: event_detail/{royal_prevented_filename}")
    
    # บันทึก HTML report metadata ลง database
    db.save_html_report(
        report_date=date_filename,
        file_name=html_filename,
        file_path=html_path,
        malicious_count=len(malicious_filtered),
        suspicious_count=len(suspicious_filtered),
        report_url=details_url
    )
    
    # 4. สร้างข้อความ Mattermost
    print("\n📝 Building Mattermost message...")
    report_date = target_date or datetime.now(TZ_BANGKOK).date()
    reports_index_url = f"{REPORT_SERVER_URL.rstrip('/')}/event_detail/"
    message = build_mattermost_message(malicious_filtered, suspicious_filtered, details_url, report_date, not_found_url, len(devices_not_found) if devices_not_found else 0, royal_detected_url, royal_prevented_url, reports_index_url)

    # บันทึก message เป็นไฟล์ .md และอัปเดต index สำหรับดูย้อนหลัง
    md_filename = f"{date_filename}-daily-report.md"
    md_path = os.path.join(EVENT_DETAIL_DIR, md_filename)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(message)
    build_reports_index(EVENT_DETAIL_DIR)
    
    # 5. แสดงตัวอย่าง
    print("\n" + "=" * 70)
    print("  📨 Preview Message:")
    print("=" * 70)
    print(message)
    print("=" * 70)

    # --debug-devices: แสดงรายการเครื่อง PREVENTED/DETECTED เพื่อเปรียบเทียบกับ export
    if '--debug-devices' in sys.argv:
        det, prev = set(), set()
        for e in malicious_filtered + suspicious_filtered:
            rec = e.get('recorded_device_info') or {}
            raw = rec.get('hostname') or rec.get('device_name') or e.get('device_name') or ''
            dn = str(raw).strip() if raw and str(raw).lower() not in ('n/a', 'none', '') else None
            if dn and e.get('action') == 'DETECTED':
                det.add(dn)
            elif dn and e.get('action') == 'PREVENTED':
                prev.add(dn)
        print("\n📋 [DEBUG] รายการเครื่องสำหรับเปรียบเทียบกับ Export:")
        print(f"   DETECTED: {len(det)} เครื่อง")
        for i, d in enumerate(sorted(det), 1):
            print(f"      {i:2}. {d}")
        print(f"   PREVENTED: {len(prev)} เครื่อง")
        for i, d in enumerate(sorted(prev), 1):
            print(f"      {i:2}. {d}")
    
    # 6. ส่งไปยัง Mattermost (ข้ามได้ด้วย --no-send สำหรับทดสอบ)
    if '--no-send' in sys.argv:
        print("\n📤 [ข้ามส่ง] ใช้ --no-send สำหรับทดสอบ (ไม่ส่งไป Mattermost)")
        success = True
    else:
        print("\n📤 Sending to Mattermost...")
        success = send_to_mattermost(message)
    
    if success:
        if '--no-send' in sys.argv:
            print("   ✅ รายงานสร้างเรียบร้อย (ไม่ได้ส่ง)")
            print(f"\n📄 Detailed report: {html_path}")
            print(f"   👑 Royal DETECTED: {os.path.join(EVENT_DETAIL_DIR, royal_detected_filename)}")
            print(f"   👑 Royal PREVENTED: {os.path.join(EVENT_DETAIL_DIR, royal_prevented_filename)}")
        else:
            print("   ✅ Sent successfully!")
            print(f"\n📄 Detailed report: {html_path}")
            # ทำเครื่องหมายว่ารายงานถูกส่งแล้ว
            db.mark_report_sent(date_filename)
    else:
        print("   ❌ Failed to send")
    
    # 7. แสดงสถิติจาก database
    print("\n📊 Database Statistics:")
    stats = db.get_statistics()
    print(f"   Total events in DB: {stats.get('total_events', 0)}")
    print(f"   By type: {stats.get('by_type', {})}")
    print(f"   Notifications: {stats.get('notifications', {})}")
    
    print("\n" + "=" * 70)
    print("  ✅ Done!")
    print("=" * 70)

if __name__ == "__main__":
    main()
