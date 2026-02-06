#!/bin/bash
# ดึง Events ของวันนี้จาก Deep Instinct API

# Load environment variables
source .env1 2>/dev/null || true

# ถ้าไม่มี TOKENS_KEY ให้ระบุด้วยตนเอง
if [ -z "$TOKENS_KEY" ]; then
    TOKENS_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2OTY2OTk1MCwianRpIjoiNzAxYjIxYmUtN2U4OC00OWFmLWE0NGUtMjI5NDU4MWViY2IwIiwidHlwZSI6ImFjY2VzcyIsImlkZW50aXR5Ijp7ImtleSI6MTR9LCJuYmYiOjE3Njk2Njk5NTB9.sOypvViOIn79Pj6caM3vg34L-Ktf741ayPYoEOOEIbM"
fi

if [ -z "$DEEPINSTINCT_URL" ]; then
    DEEPINSTINCT_URL="https://ro.customers.deepinstinctweb.com/api/v1/"
fi

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          Fetch Today's Events from Deep Instinct            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📅 วันที่: $(date '+%Y-%m-%d (%d/%m/%Y)')"
echo "🔗 API URL: $DEEPINSTINCT_URL"
echo ""

# ดึง events ด้วย curl
curl -s -X GET "${DEEPINSTINCT_URL}events/" \
  -H "accept: application/json" \
  -H "Authorization: $TOKENS_KEY" \
  | python3 << 'PYTHON_SCRIPT'
import sys
import json
from datetime import datetime

try:
    data = json.load(sys.stdin)
    
    # Extract events
    if isinstance(data, dict):
        events = data.get('events', [])
        last_id = data.get('last_id', 'N/A')
    else:
        events = data
        last_id = 'N/A'
    
    # วันที่วันนี้
    today = datetime.now().strftime('%Y-%m-%d')
    
    print('=' * 60)
    print(f'📊 จำนวน events ทั้งหมด: {len(events)}')
    print(f'🆔 Last ID: {last_id}')
    print('=' * 60)
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
        print(f'✅ พบ {len(filtered)} events ในวันนี้ ({today})')
        print()
        print('=' * 60)
        print('📋 รายละเอียด Events:')
        print('=' * 60)
        
        for i, event in enumerate(filtered, 1):
            ts = event.get('timestamp') or event.get('recorded_device_timestamp')
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            
            print(f'\n[{i}] Event ID: {event.get("id", "N/A")}')
            print(f'    📅 วันที่-เวลา: {dt.strftime("%Y-%m-%d %H:%M:%S")}')
            print(f'    📊 Type: {event.get("type", "N/A")}')
            print(f'    🎯 Severity: {event.get("severity", "N/A")}')
            print(f'    ✓ Status: {event.get("status", "N/A")}')
            print(f'    🔧 Action: {event.get("action", "N/A")}')
            print(f'    💻 Device: {event.get("device_name", "N/A")}')
            print(f'    🖥️  OS: {event.get("os", "N/A")}')
            print(f'    📄 File: {event.get("file_name", "N/A")}')
            
            if event.get('path'):
                print(f'    📂 Path: {event.get("path")}')
            
            if event.get('file_hash'):
                hash_val = event.get('file_hash')
                display_hash = f"{hash_val[:32]}..." if len(hash_val) > 32 else hash_val
                print(f'    🔐 Hash: {display_hash}')
        
        print()
        print('=' * 60)
        print(f'✅ สรุป: พบ {len(filtered)} events ในวันนี้')
        print('=' * 60)
    else:
        print(f'❌ ไม่พบ events ในวันนี้ ({today})')
        print()
        print('ℹ️  Events ล่าสุดในระบบ (5 รายการ):')
        print('-' * 60)
        
        for i, event in enumerate(events[:5], 1):
            ts = event.get('timestamp') or event.get('recorded_device_timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    print(f'  [{i}] ID: {event.get("id")} - {dt.strftime("%Y-%m-%d %H:%M:%S")}')
                    print(f'      Type: {event.get("type")} | Status: {event.get("status")}')
                except:
                    pass

except json.JSONDecodeError as e:
    print(f'❌ Error parsing JSON: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
PYTHON_SCRIPT

echo ""
echo "✅ เสร็จสิ้น"
