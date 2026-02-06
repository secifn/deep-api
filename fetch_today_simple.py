#!/usr/bin/env python3
"""ดึง Events ของวันนี้จาก Deep Instinct"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env1')

print("╔══════════════════════════════════════════════════════════════╗")
print("║          Fetch Today's Events from Deep Instinct            ║")
print("╚══════════════════════════════════════════════════════════════╝")
print()

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')
today_display = datetime.now().strftime('%d/%m/%Y')

print(f"📅 วันที่: {today} ({today_display})")
print()

# API call
url = os.getenv('DEEPINSTINCT_URL').rstrip('/') + '/events/'
token = os.getenv('TOKENS_KEY')

response = requests.get(url, headers={'Authorization': token}, timeout=30)

if response.status_code == 200:
    result = response.json()
    
    if isinstance(result, dict):
        events = result.get('events', [])
        last_id = result.get('last_id', 'N/A')
    else:
        events = result
        last_id = 'N/A'
    
    print("=" * 60)
    print(f"📊 จำนวน events ทั้งหมด: {len(events)}")
    print(f"🆔 Last ID: {last_id}")
    print("=" * 60)
    print()
    
    # Filter events ของวันนี้
    filtered = []
    for event in events:
        ts = event.get('timestamp') or event.get('recorded_device_timestamp')
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                if dt.strftime('%Y-%m-%d') == today:
                    filtered.append(event)
            except:
                pass
    
    if filtered:
        print(f"✅ พบ {len(filtered)} events ในวันนี้ ({today})")
        print()
        print("=" * 60)
        print("📋 รายละเอียด Events:")
        print("=" * 60)
        
        for i, event in enumerate(filtered, 1):
            ts = event.get('timestamp') or event.get('recorded_device_timestamp')
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            
            print(f"\n[{i}] Event ID: {event.get('id', 'N/A')}")
            print(f"    📅 วันที่-เวลา: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    📊 Type: {event.get('type', 'N/A')}")
            print(f"    🎯 Severity: {event.get('severity', 'N/A')}")
            print(f"    ✓ Status: {event.get('status', 'N/A')}")
            print(f"    🔧 Action: {event.get('action', 'N/A')}")
            print(f"    💻 Device: {event.get('device_name', 'N/A')}")
            print(f"    🖥️  OS: {event.get('os', 'N/A')}")
            print(f"    📄 File: {event.get('file_name', 'N/A')}")
            
            if event.get('path'):
                print(f"    📂 Path: {event.get('path')}")
            
            if event.get('file_hash'):
                hash_val = event.get('file_hash')
                display_hash = f"{hash_val[:32]}..." if len(hash_val) > 32 else hash_val
                print(f"    🔐 Hash: {display_hash}")
        
        print()
        print("=" * 60)
        print(f"✅ สรุป: พบ {len(filtered)} events ในวันนี้")
        print("=" * 60)
    else:
        print(f"❌ ไม่พบ events ในวันนี้ ({today})")
        print()
        print("ℹ️  Events ล่าสุดในระบบ (5 รายการ):")
        print("-" * 60)
        
        for i, event in enumerate(events[:5], 1):
            ts = event.get('timestamp') or event.get('recorded_device_timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    print(f"  [{i}] ID: {event.get('id')} - {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"      Type: {event.get('type')} | Status: {event.get('status')}")
                except:
                    pass
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text[:500])
