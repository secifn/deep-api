#!/usr/bin/env python3
"""
สคริปต์สำหรับดึงข้อมูล Events จาก Deep Instinct และส่งไปยัง Mattermost แบบครั้งเดียว
เหมาะสำหรับการทดสอบหรือดึงข้อมูลย้อนหลัง
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Import classes จากสคริปต์หลัก
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deepinstinct_to_mattermost import DeepInstinctClient, MattermostNotifier, DeepInstinctMonitor

# โหลด environment variables
load_dotenv('.env1')


def main():
    parser = argparse.ArgumentParser(
        description='ดึงข้อมูล Events จาก Deep Instinct และส่งไปยัง Mattermost แบบครั้งเดียว',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # ดึง events ทั้งหมด
  python fetch_events_once.py
  
  # ดึง events หลัง ID 12345
  python fetch_events_once.py --after-id 12345
  
  # ดึงเฉพาะ events (ไม่รวม suspicious events)
  python fetch_events_once.py --events-only
  
  # ดึงเฉพาะ suspicious events (ไม่รวม events)
  python fetch_events_once.py --suspicious-only
  
  # ดึงและแสดงเฉพาะใน terminal (ไม่ส่งไปยัง Mattermost)
  python fetch_events_once.py --dry-run
        """
    )
    
    parser.add_argument(
        '--after-id',
        type=int,
        default=0,
        help='ดึง events หลัง ID นี้ (default: 0 = ดึงทั้งหมด)'
    )
    
    parser.add_argument(
        '--events-only',
        action='store_true',
        help='ดึงเฉพาะ events (ไม่รวม suspicious events)'
    )
    
    parser.add_argument(
        '--suspicious-only',
        action='store_true',
        help='ดึงเฉพาะ suspicious events (ไม่รวม events)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='แสดงข้อมูลใน terminal เท่านั้น (ไม่ส่งไปยัง Mattermost)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='จำนวน events สูงสุดที่จะดึง (default: 50)'
    )
    
    args = parser.parse_args()
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║      Fetch Deep Instinct Events - One Time Execution        ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    # ตรวจสอบ Environment Variables
    di_url = os.getenv('DEEPINSTINCT_URL')
    di_token = os.getenv('TOKENS_KEY')
    mm_webhook = os.getenv('MATTERMOST_WEBHOOK_URL')
    
    if not di_url or not di_token:
        print("❌ Error: Missing Deep Instinct credentials in .env1")
        print("   Required: DEEPINSTINCT_URL, TOKENS_KEY")
        return 1
    
    if not args.dry_run and not mm_webhook:
        print("❌ Error: Missing MATTERMOST_WEBHOOK_URL in .env1")
        print("   Tip: Use --dry-run to test without sending to Mattermost")
        return 1
    
    print(f"✅ Deep Instinct URL: {di_url}")
    print(f"✅ After Event ID: {args.after_id}")
    print(f"✅ Limit: {args.limit}")
    
    if args.dry_run:
        print("🧪 Mode: DRY RUN (ไม่ส่งไปยัง Mattermost)")
    else:
        print(f"✅ Mattermost Webhook: {mm_webhook[:50]}...")
    
    print()
    
    # สร้าง clients
    di_client = DeepInstinctClient(di_url, di_token)
    mm_notifier = MattermostNotifier(mm_webhook) if not args.dry_run else None
    
    total_events = 0
    total_suspicious = 0
    
    # ดึง Events
    if not args.suspicious_only:
        print("=" * 60)
        print("📥 Fetching Events...")
        print("=" * 60)
        
        events = di_client.get_events(after_event_id=args.after_id, limit=args.limit)
        
        if events:
            print(f"✅ Found {len(events)} event(s)\n")
            total_events = len(events)
            
            for i, event in enumerate(events, 1):
                print(f"\n[{i}/{len(events)}] Event ID: {event.get('id', 'N/A')}")
                print("-" * 60)
                
                # แสดงข้อมูลสำคัญ
                important_fields = [
                    'id', 'type', 'severity', 'status', 'action',
                    'device_name', 'os', 'file_name', 'path', 'file_hash',
                    'timestamp', 'recorded_device_timestamp'
                ]
                
                for field in important_fields:
                    if field in event:
                        value = event[field]
                        if field == 'file_hash' and value:
                            value = f"{value[:32]}..." if len(value) > 32 else value
                        print(f"  {field:25s}: {value}")
                
                # ส่งไปยัง Mattermost ถ้าไม่ใช่ dry-run
                if not args.dry_run and mm_notifier:
                    attachment = mm_notifier.format_event_message(event, "Event")
                    if mm_notifier.send_message('', attachments=[attachment]):
                        print(f"  ✉️  Sent to Mattermost")
                    else:
                        print(f"  ⚠️  Failed to send to Mattermost")
        else:
            print("ℹ️  No events found")
    
    # ดึง Suspicious Events
    if not args.events_only:
        print("\n" + "=" * 60)
        print("📥 Fetching Suspicious Events...")
        print("=" * 60)
        
        suspicious_events = di_client.get_suspicious_events(after_event_id=args.after_id)
        
        if suspicious_events:
            print(f"✅ Found {len(suspicious_events)} suspicious event(s)\n")
            total_suspicious = len(suspicious_events)
            
            for i, event in enumerate(suspicious_events, 1):
                print(f"\n[{i}/{len(suspicious_events)}] Suspicious Event ID: {event.get('id', 'N/A')}")
                print("-" * 60)
                
                # แสดงข้อมูลสำคัญ
                important_fields = [
                    'id', 'type', 'severity', 'status', 'action',
                    'device_name', 'os', 'file_name', 'path', 'file_hash',
                    'timestamp', 'recorded_device_timestamp'
                ]
                
                for field in important_fields:
                    if field in event:
                        value = event[field]
                        if field == 'file_hash' and value:
                            value = f"{value[:32]}..." if len(value) > 32 else value
                        print(f"  {field:25s}: {value}")
                
                # ส่งไปยัง Mattermost ถ้าไม่ใช่ dry-run
                if not args.dry_run and mm_notifier:
                    attachment = mm_notifier.format_event_message(event, "Suspicious Event")
                    if mm_notifier.send_message('', attachments=[attachment]):
                        print(f"  ✉️  Sent to Mattermost")
                    else:
                        print(f"  ⚠️  Failed to send to Mattermost")
        else:
            print("ℹ️  No suspicious events found")
    
    # สรุปผล
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"Total Events: {total_events}")
    print(f"Total Suspicious Events: {total_suspicious}")
    print(f"Total: {total_events + total_suspicious}")
    
    if args.dry_run:
        print("\n🧪 This was a DRY RUN - no data was sent to Mattermost")
    else:
        print("\n✅ Data sent to Mattermost")
    
    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
