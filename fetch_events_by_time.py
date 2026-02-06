#!/usr/bin/env python3
"""
ดึง Events จาก Deep Instinct ตามช่วงเวลาที่กำหนด
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv('.env1')

def fetch_events_by_timerange(start_hour, end_hour, date=None):
    """
    ดึง events ตามช่วงเวลา
    
    Args:
        start_hour: ชั่วโมงเริ่มต้น (0-23)
        end_hour: ชั่วโมงสิ้นสุด (0-23)
        date: วันที่ (YYYY-MM-DD) ถ้าไม่ระบุจะใช้วันนี้
    """
    di_url = os.getenv('DEEPINSTINCT_URL')
    di_token = os.getenv('TOKENS_KEY')
    
    if not di_url or not di_token:
        print("❌ Error: Missing Deep Instinct credentials in .env1")
        return []
    
    # สร้าง timestamp range
    if date is None:
        today = datetime.now()
    else:
        today = datetime.strptime(date, '%Y-%m-%d')
    
    start_time = today.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end_time = today.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    
    # แปลงเป็น ISO 8601 format
    from_timestamp = start_time.isoformat() + 'Z'
    to_timestamp = end_time.isoformat() + 'Z'
    
    print("=" * 60)
    print(f"🔍 ดึง Events จาก Deep Instinct")
    print("=" * 60)
    print(f"ช่วงเวลา: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {di_url}")
    print()
    
    # วิธีที่ 1: ลองใช้ search endpoint
    try:
        url = f"{di_url.rstrip('/')}/events/search"
        headers = {
            'Authorization': di_token,
            'Content-Type': 'application/json'
        }
        
        # Search payload
        payload = {
            "timestamp": {
                "from": from_timestamp,
                "to": to_timestamp
            }
        }
        
        print(f"📡 Searching events with timestamp filter...")
        print(f"Payload: {payload}")
        print()
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, dict):
                events = result.get('events', [])
                last_id = result.get('last_id', 'N/A')
                print(f"✅ พบ {len(events)} event(s)")
                print(f"Last ID: {last_id}")
            elif isinstance(result, list):
                events = result
                print(f"✅ พบ {len(events)} event(s)")
            else:
                events = []
                print(f"⚠️  Response format ไม่คาดคิด")
            
            return events
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            # ถ้า search ไม่ได้ ลองดึงทั้งหมดแล้ว filter ใน Python
            print("\n" + "=" * 60)
            print("🔄 พยายามดึงทั้งหมดแล้ว filter ใน Python...")
            print("=" * 60)
            return fetch_all_and_filter(di_url, di_token, start_time, end_time)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n" + "=" * 60)
        print("🔄 พยายามดึงทั้งหมดแล้ว filter ใน Python...")
        print("=" * 60)
        return fetch_all_and_filter(di_url, di_token, start_time, end_time)


def fetch_all_and_filter(di_url, di_token, start_time, end_time):
    """ดึง events ทั้งหมดแล้ว filter ตาม timestamp"""
    try:
        url = f"{di_url.rstrip('/')}/events/"
        headers = {
            'Authorization': di_token,
            'Content-Type': 'application/json'
        }
        
        print(f"📡 Fetching all events...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, dict):
                all_events = result.get('events', [])
            elif isinstance(result, list):
                all_events = result
            else:
                print(f"⚠️  Response format ไม่คาดคิด")
                return []
            
            print(f"📊 ดึงได้ทั้งหมด {len(all_events)} events")
            print(f"🔍 กำลัง filter ตามช่วงเวลา...")
            
            # Filter events by timestamp
            filtered_events = []
            for event in all_events:
                event_time_str = event.get('timestamp') or event.get('recorded_device_timestamp')
                if event_time_str:
                    try:
                        # Parse timestamp (รองรับหลายรูปแบบ)
                        event_time = datetime.fromisoformat(event_time_str.replace('Z', '+00:00'))
                        
                        # เปรียบเทียบเวลา (ignore timezone)
                        event_time_naive = event_time.replace(tzinfo=None)
                        
                        if start_time <= event_time_naive <= end_time:
                            filtered_events.append(event)
                    except Exception as e:
                        pass
            
            print(f"✅ พบ {len(filtered_events)} event(s) ในช่วงเวลาที่กำหนด")
            return filtered_events
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return []
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def display_events(events):
    """แสดง events"""
    if not events:
        print("\n❌ ไม่พบ events ในช่วงเวลานี้")
        return
    
    print("\n" + "=" * 60)
    print(f"📋 Events ที่พบ ({len(events)} รายการ)")
    print("=" * 60)
    
    for i, event in enumerate(events, 1):
        print(f"\n[{i}] Event ID: {event.get('id', 'N/A')}")
        print("-" * 60)
        
        # ข้อมูลสำคัญ
        fields = [
            ('Type', event.get('type')),
            ('Severity', event.get('severity')),
            ('Status', event.get('status')),
            ('Action', event.get('action')),
            ('Device', event.get('device_name')),
            ('OS', event.get('os')),
            ('File Name', event.get('file_name')),
            ('Path', event.get('path')),
            ('File Hash', event.get('file_hash', '')[:32] + '...' if event.get('file_hash') else 'N/A'),
            ('Timestamp', event.get('timestamp')),
            ('Device Timestamp', event.get('recorded_device_timestamp')),
        ]
        
        for label, value in fields:
            if value:
                print(f"  {label:20s}: {value}")


def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         Fetch Deep Instinct Events by Time Range            ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    # ดึง events ช่วง 12:00-15:00
    events = fetch_events_by_timerange(
        start_hour=12,
        end_hour=15,
        date=None  # วันนี้
    )
    
    # แสดงผลลัพธ์
    display_events(events)
    
    # ถามว่าจะส่งไปยัง Mattermost หรือไม่
    if events:
        print("\n" + "=" * 60)
        print("📨 ต้องการส่ง events เหล่านี้ไปยัง Mattermost หรือไม่?")
        print("=" * 60)
        print(f"จำนวน events: {len(events)}")
        print("\nรันคำสั่ง:")
        print("  python3 send_events_to_mattermost.py")
        print("\nหรือรันแบบอัตโนมัติ:")
        print("  python3 deepinstinct_to_mattermost.py")


if __name__ == '__main__':
    main()
