#!/usr/bin/env python3
"""
Deep Instinct to Mattermost Integration Script
ดึงข้อมูล Events และ Suspicious Events จาก Deep Instinct API และส่งไปยัง Mattermost Webhook
พร้อมป้องกันการส่งซ้ำด้วย SQLite database
"""

import os
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from database import get_db

# โหลด environment variables
load_dotenv('.env1')

class DeepInstinctClient:
    """Client สำหรับเชื่อมต่อกับ Deep Instinct API"""
    
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': api_token,  # Deep Instinct doesn't use "Bearer " prefix
            'Content-Type': 'application/json'
        }
        self.last_event_id = 0
        self.last_suspicious_event_id = 0
    
    def get_events(self, after_event_id: int = 0, limit: int = 50) -> List[Dict]:
        """
        ดึงข้อมูล Events จาก Deep Instinct
        
        Args:
            after_event_id: Event ID ที่จะเริ่มดึงข้อมูลหลังจาก ID นี้
            limit: จำนวน events ที่ต้องการดึง (default: 50)
        
        Returns:
            List ของ events
        """
        try:
            url = f"{self.base_url}/events/"
            params = {'after_event_id': after_event_id} if after_event_id > 0 else {}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Handle both list and dict responses
            if isinstance(result, dict):
                events = result.get('events', [])
            elif isinstance(result, list):
                events = result
            else:
                events = []
            
            return events
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching events: {e}")
            return []
    
    def get_suspicious_events(self, after_event_id: int = 0) -> List[Dict]:
        """
        ดึงข้อมูล Suspicious Events จาก Deep Instinct
        
        Args:
            after_event_id: Event ID ที่จะเริ่มดึงข้อมูลหลังจาก ID นี้
        
        Returns:
            List ของ suspicious events
        """
        try:
            url = f"{self.base_url}/suspicious-events/"
            params = {'after_event_id': after_event_id} if after_event_id > 0 else {}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            events = response.json()
            return events if isinstance(events, list) else []
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching suspicious events: {e}")
            return []
    
    def search_events(self, search_criteria: Dict) -> List[Dict]:
        """
        ค้นหา Events ด้วยเงื่อนไขที่กำหนด
        
        Args:
            search_criteria: Dictionary ของเงื่อนไขในการค้นหา
        
        Returns:
            List ของ events ที่ตรงกับเงื่อนไข
        """
        try:
            url = f"{self.base_url}/events/search"
            response = requests.post(url, headers=self.headers, json=search_criteria, timeout=30)
            response.raise_for_status()
            
            events = response.json()
            return events if isinstance(events, list) else []
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error searching events: {e}")
            return []
    
    def get_event_details(self, event_id: int) -> Optional[Dict]:
        """
        ดึงรายละเอียดของ Event ตาม ID
        
        Args:
            event_id: ID ของ event
        
        Returns:
            Dictionary ของรายละเอียด event หรือ None ถ้าไม่พบ
        """
        try:
            url = f"{self.base_url}/events/{event_id}"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching event details for ID {event_id}: {e}")
            return None


class MattermostNotifier:
    """Client สำหรับส่ง notifications ไปยัง Mattermost"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_message(self, text: str, attachments: Optional[List[Dict]] = None) -> bool:
        """
        ส่งข้อความไปยัง Mattermost
        
        Args:
            text: ข้อความหลัก
            attachments: List ของ attachments (optional)
        
        Returns:
            True ถ้าส่งสำเร็จ, False ถ้าล้มเหลว
        """
        try:
            payload = {'text': text}
            if attachments:
                payload['attachments'] = attachments
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending to Mattermost: {e}")
            return False
    
    def format_event_message(self, event: Dict, event_type: str = "Event") -> Dict:
        """
        จัดรูปแบบ event เป็น Mattermost attachment
        
        Args:
            event: Dictionary ของ event data
            event_type: ประเภทของ event (Event หรือ Suspicious Event)
        
        Returns:
            Dictionary ของ Mattermost attachment
        """
        # กำหนดสีตามความรุนแรง
        severity = event.get('severity', 'UNKNOWN').upper()
        color_map = {
            'CRITICAL': '#FF0000',  # แดง
            'HIGH': '#FF6600',      # ส้ม
            'MEDIUM': '#FFD700',    # เหลือง
            'LOW': '#00FF00',       # เขียว
            'INFO': '#0099FF'       # น้ำเงิน
        }
        color = color_map.get(severity, '#808080')
        
        # สร้าง fields สำหรับแสดงข้อมูล
        fields = []
        
        # ข้อมูลพื้นฐาน
        if 'id' in event:
            fields.append({
                'short': True,
                'title': 'Event ID',
                'value': str(event['id'])
            })
        
        if 'type' in event:
            fields.append({
                'short': True,
                'title': 'Type',
                'value': event['type']
            })
        
        if 'severity' in event:
            fields.append({
                'short': True,
                'title': 'Severity',
                'value': event['severity']
            })
        
        if 'status' in event:
            fields.append({
                'short': True,
                'title': 'Status',
                'value': event['status']
            })
        
        # ข้อมูลอุปกรณ์
        if 'device_name' in event:
            fields.append({
                'short': True,
                'title': 'Device',
                'value': event['device_name']
            })
        
        if 'os' in event:
            fields.append({
                'short': True,
                'title': 'OS',
                'value': event['os']
            })
        
        # ข้อมูลไฟล์/ภัยคุกคาม
        if 'file_name' in event:
            fields.append({
                'short': False,
                'title': 'File Name',
                'value': event['file_name']
            })
        
        if 'path' in event:
            fields.append({
                'short': False,
                'title': 'Path',
                'value': event['path']
            })
        
        if 'file_hash' in event:
            fields.append({
                'short': False,
                'title': 'File Hash',
                'value': f"`{event['file_hash']}`"
            })
        
        # วันที่/เวลา
        if 'timestamp' in event:
            fields.append({
                'short': True,
                'title': 'Timestamp',
                'value': event['timestamp']
            })
        
        if 'recorded_device_timestamp' in event:
            fields.append({
                'short': True,
                'title': 'Device Time',
                'value': event['recorded_device_timestamp']
            })
        
        # ข้อมูลเพิ่มเติม
        if 'comment' in event and event['comment']:
            fields.append({
                'short': False,
                'title': 'Comment',
                'value': event['comment']
            })
        
        # สร้าง attachment
        attachment = {
            'color': color,
            'pretext': f'🚨 **New {event_type} Detected**',
            'fields': fields,
            'footer': 'Deep Instinct Security',
            'footer_icon': 'https://www.deepinstinct.com/favicon.ico',
            'ts': int(time.time())
        }
        
        return attachment


class DeepInstinctMonitor:
    """Monitor สำหรับตรวจสอบและส่ง events ไปยัง Mattermost"""
    
    def __init__(self, di_client: DeepInstinctClient, mm_notifier: MattermostNotifier):
        self.di_client = di_client
        self.mm_notifier = mm_notifier
        self.last_event_id = 0
        self.last_suspicious_event_id = 0
        self.db = get_db()  # Database instance
    
    def process_events(self, events: List[Dict], event_type: str = "Event") -> int:
        """
        ประมวลผลและส่ง events ไปยัง Mattermost (พร้อมป้องกันส่งซ้ำ)
        
        Args:
            events: List ของ events
            event_type: ประเภทของ event
        
        Returns:
            จำนวน events ที่ส่งสำเร็จ
        """
        count = 0
        skipped = 0
        
        for event in events:
            try:
                event_id = event.get('id')
                if not event_id:
                    continue
                
                # เช็คว่าเคยส่งแล้วหรือไม่
                event_type_db = 'malicious' if event_type == 'Event' else 'suspicious'
                
                # บันทึก event ลง database ก่อน (จะ skip ถ้ามีอยู่แล้ว)
                saved = self.db.save_event(event, event_type_db)
                
                # ถ้า event มีอยู่แล้วและเคยส่ง notification แล้ว ให้ skip
                if not saved and self.db.event_exists(event_id, event_type_db):
                    # เช็คว่าเคยส่ง notification หรือยัง
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT notified FROM events 
                            WHERE event_id = ? AND event_type = ?
                        """, (event_id, event_type_db))
                        result = cursor.fetchone()
                        
                        if result and result[0] == 1:
                            skipped += 1
                            print(f"⏭️  Skipped {event_type} ID: {event_id} (already notified)")
                            continue
                
                # ส่งไปยัง Mattermost
                attachment = self.mm_notifier.format_event_message(event, event_type)
                
                if self.mm_notifier.send_message('', attachments=[attachment]):
                    count += 1
                    print(f"✅ Sent {event_type} ID: {event_id}")
                    
                    # ทำเครื่องหมายว่าส่งแล้ว
                    self.db.mark_as_notified(event_id, 'mattermost', success=True)
                else:
                    print(f"⚠️  Failed to send {event_type} ID: {event_id}")
                    self.db.mark_as_notified(event_id, 'mattermost', success=False, 
                                            error_message="Failed to send to Mattermost")
                
                # หน่วงเวลาเล็กน้อยเพื่อไม่ให้ spam
                time.sleep(0.5)
            
            except Exception as e:
                print(f"❌ Error processing event: {e}")
                if event_id:
                    self.db.mark_as_notified(event_id, 'mattermost', success=False, 
                                            error_message=str(e))
        
        if skipped > 0:
            print(f"📊 Summary: {count} sent, {skipped} skipped (duplicates)")
        
        return count
    
    def check_new_events(self) -> tuple:
        """
        ตรวจสอบ events และ suspicious events ใหม่
        
        Returns:
            Tuple ของ (จำนวน events, จำนวน suspicious events) ที่พบ
        """
        # ดึง Events ใหม่
        print(f"\n🔍 Checking for new events (after ID: {self.last_event_id})...")
        events = self.di_client.get_events(after_event_id=self.last_event_id)
        
        if events:
            print(f"📊 Found {len(events)} new event(s)")
            sent = self.process_events(events, "Event")
            print(f"✉️  Sent {sent}/{len(events)} events to Mattermost")
            
            # อัพเดท last event ID
            if events and 'id' in events[-1]:
                self.last_event_id = events[-1]['id']
        else:
            print("ℹ️  No new events found")
        
        # ดึง Suspicious Events ใหม่
        print(f"\n🔍 Checking for new suspicious events (after ID: {self.last_suspicious_event_id})...")
        suspicious_events = self.di_client.get_suspicious_events(
            after_event_id=self.last_suspicious_event_id
        )
        
        if suspicious_events:
            print(f"📊 Found {len(suspicious_events)} new suspicious event(s)")
            sent = self.process_events(suspicious_events, "Suspicious Event")
            print(f"✉️  Sent {sent}/{len(suspicious_events)} suspicious events to Mattermost")
            
            # อัพเดท last suspicious event ID
            if suspicious_events and 'id' in suspicious_events[-1]:
                self.last_suspicious_event_id = suspicious_events[-1]['id']
        else:
            print("ℹ️  No new suspicious events found")
        
        return len(events), len(suspicious_events)
    
    def run_continuous(self, interval: int = 300):
        """
        รันการตรวจสอบแบบต่อเนื่อง
        
        Args:
            interval: ระยะเวลาระหว่างการตรวจสอบ (วินาที) default: 300 วินาที (5 นาที)
        """
        print("🚀 Starting Deep Instinct Monitor...")
        print(f"⏱️  Polling interval: {interval} seconds ({interval/60:.1f} minutes)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n{'='*60}")
                print(f"🕐 {timestamp}")
                print(f"{'='*60}")
                
                self.check_new_events()
                
                print(f"\n💤 Sleeping for {interval} seconds...")
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n👋 Stopping monitor... Goodbye!")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")


def main():
    """Main function"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   Deep Instinct to Mattermost Integration                   ║")
    print("║   ดึงข้อมูล Security Events และส่งไปยัง Mattermost          ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    # ตรวจสอบ Environment Variables
    di_url = os.getenv('DEEPINSTINCT_URL')
    di_token = os.getenv('TOKENS_KEY')
    mm_webhook = os.getenv('MATTERMOST_WEBHOOK_URL')
    
    if not di_url or not di_token:
        print("❌ Error: Missing Deep Instinct credentials in .env1")
        print("   Required: DEEPINSTINCT_URL, TOKENS_KEY")
        return
    
    if not mm_webhook:
        print("❌ Error: Missing MATTERMOST_WEBHOOK_URL in environment")
        print("   Please set MATTERMOST_WEBHOOK_URL in .env1 file")
        print("\n   Example:")
        print("   MATTERMOST_WEBHOOK_URL=https://your-mattermost-server.com/hooks/xxx-your-hook-id-xxx")
        return
    
    print(f"✅ Deep Instinct URL: {di_url}")
    print(f"✅ Token: {di_token[:20]}...")
    print(f"✅ Mattermost Webhook: {mm_webhook[:50]}...")
    print()
    
    # สร้าง clients
    di_client = DeepInstinctClient(di_url, di_token)
    mm_notifier = MattermostNotifier(mm_webhook)
    
    # ทดสอบการเชื่อมต่อ
    print("🔌 Testing connection to Deep Instinct API...")
    test_events = di_client.get_events(limit=1)
    if test_events is not None:
        print("✅ Connected to Deep Instinct API successfully!")
    else:
        print("⚠️  Warning: Could not verify Deep Instinct API connection")
    
    print("\n🔌 Testing connection to Mattermost...")
    if mm_notifier.send_message("🚀 Deep Instinct Monitor is starting up!"):
        print("✅ Connected to Mattermost successfully!")
    else:
        print("⚠️  Warning: Could not verify Mattermost webhook")
    
    # สร้าง monitor และรัน
    monitor = DeepInstinctMonitor(di_client, mm_notifier)
    
    # ดึงข้อมูลครั้งแรก
    print("\n📥 Fetching initial events...")
    monitor.check_new_events()
    
    # รันแบบต่อเนื่อง (polling ทุก 5 นาที)
    # แก้ไข interval ตามต้องการ เช่น 60 = 1 นาที, 300 = 5 นาที, 600 = 10 นาที
    polling_interval = int(os.getenv('POLLING_INTERVAL', '300'))
    monitor.run_continuous(interval=polling_interval)


if __name__ == '__main__':
    main()
