#!/usr/bin/env python3
"""
Database Manager for Deep Instinct Events
จัดการ SQLite database สำหรับเก็บ event history และ HTML reports
"""

import sqlite3
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
from pathlib import Path


class DatabaseManager:
    """จัดการ SQLite database สำหรับ Deep Instinct events"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file (default: ./data/events.db)
        """
        if db_path is None:
            # ใช้โฟลเดอร์ data/ ใน project root
            script_dir = Path(__file__).parent
            data_dir = script_dir / 'data'
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / 'events.db')
        
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager สำหรับ database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # ให้ access columns ด้วยชื่อได้
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """สร้าง database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table: events - เก็บ event หลักจาก Deep Instinct
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    event_id INTEGER UNIQUE NOT NULL,
                    event_type TEXT NOT NULL,
                    threat_type TEXT,
                    threat_severity TEXT,
                    action TEXT,
                    status TEXT,
                    description TEXT,
                    
                    -- Device information
                    device_name TEXT,
                    hostname TEXT,
                    ip_address TEXT,
                    os TEXT,
                    
                    -- Organization
                    msp_name TEXT,
                    tenant_name TEXT,
                    
                    -- File information
                    file_name TEXT,
                    file_path TEXT,
                    file_hash TEXT,
                    container_hash TEXT,
                    
                    -- Snip IT integration
                    responsible_person TEXT,
                    department TEXT,
                    division TEXT,
                    
                    -- Timestamps
                    timestamp TEXT NOT NULL,
                    recorded_device_timestamp TEXT,
                    insertion_timestamp TEXT,
                    created_at TEXT NOT NULL,
                    
                    -- Notification tracking
                    notified INTEGER DEFAULT 0,
                    notified_at TEXT,
                    notification_count INTEGER DEFAULT 0,
                    
                    -- Raw data
                    raw_data TEXT,
                    
                    -- Indexes
                    UNIQUE(event_id, event_type)
                )
            """)
            
            # Table: html_reports - เก็บข้อมูล HTML reports
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS html_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_date TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    
                    -- Statistics
                    malicious_count INTEGER DEFAULT 0,
                    suspicious_count INTEGER DEFAULT 0,
                    total_events INTEGER DEFAULT 0,
                    
                    -- Report metadata
                    generated_at TEXT NOT NULL,
                    sent_to_mattermost INTEGER DEFAULT 0,
                    mattermost_sent_at TEXT,
                    
                    -- Report URL
                    report_url TEXT,
                    
                    UNIQUE(report_date, file_name)
                )
            """)
            
            # Table: notification_log - เก็บประวัติการส่ง notification
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    sent_at TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    error_message TEXT,
                    
                    FOREIGN KEY (event_id) REFERENCES events(event_id)
                )
            """)
            
            # Indexes สำหรับ performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_event_id 
                ON events(event_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_timestamp 
                ON events(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_type_severity 
                ON events(event_type, threat_severity)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_notified 
                ON events(notified)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_html_reports_date 
                ON html_reports(report_date)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notification_log_event 
                ON notification_log(event_id, sent_at)
            """)
    
    def save_event(self, event: Dict, event_type: str = 'malicious', 
                   snip_it_info: Dict = None) -> bool:
        """
        บันทึก event ลง database
        
        Args:
            event: Event data จาก Deep Instinct API
            event_type: ประเภท event (malicious/suspicious)
            snip_it_info: ข้อมูลจาก Snip IT (optional)
        
        Returns:
            True ถ้าบันทึกสำเร็จ, False ถ้ามีอยู่แล้ว
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Extract device info
                recorded_info = event.get('recorded_device_info', {})
                
                # Prepare Snip IT data
                responsible = None
                department = None
                division = None
                if snip_it_info:
                    responsible = snip_it_info.get('responsible')
                    department = snip_it_info.get('แผนก')
                    division = snip_it_info.get('กอง')
                
                cursor.execute("""
                    INSERT OR IGNORE INTO events (
                        event_id, event_type, threat_type, threat_severity,
                        action, status, description,
                        device_name, hostname, ip_address, os,
                        msp_name, tenant_name,
                        file_name, file_path, file_hash, container_hash,
                        responsible_person, department, division,
                        timestamp, recorded_device_timestamp, insertion_timestamp,
                        created_at, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.get('id'),
                    event_type,
                    event.get('threat_type'),
                    event.get('threat_severity'),
                    event.get('action'),
                    event.get('status'),
                    event.get('description'),
                    recorded_info.get('device_name'),
                    recorded_info.get('hostname'),
                    recorded_info.get('ip_address'),
                    recorded_info.get('os'),
                    event.get('msp_name'),
                    event.get('tenant_name'),
                    event.get('file_name'),
                    event.get('path'),
                    event.get('file_hash'),
                    event.get('container_hash'),
                    responsible,
                    department,
                    division,
                    event.get('timestamp'),
                    event.get('recorded_device_timestamp'),
                    event.get('insertion_timestamp'),
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(event, ensure_ascii=False, default=str)
                ))
                
                return cursor.rowcount > 0
        
        except sqlite3.IntegrityError:
            # Event มีอยู่แล้ว
            return False
        except Exception as e:
            print(f"❌ Error saving event {event.get('id')}: {e}")
            return False
    
    def save_events_batch(self, events: List[Dict], event_type: str = 'malicious',
                         snip_it_lookup: Dict = None) -> Tuple[int, int]:
        """
        บันทึก events หลายรายการพร้อมกัน
        
        Args:
            events: List ของ events
            event_type: ประเภท event
            snip_it_lookup: Dictionary สำหรับ lookup Snip IT info
        
        Returns:
            Tuple (saved_count, skipped_count)
        """
        saved = 0
        skipped = 0
        
        for event in events:
            # Get Snip IT info
            snip_it_info = None
            if snip_it_lookup:
                recorded_info = event.get('recorded_device_info', {})
                hostname = recorded_info.get('hostname', '').strip().lower()
                if hostname:
                    snip_it_info = snip_it_lookup.get(hostname)
            
            if self.save_event(event, event_type, snip_it_info):
                saved += 1
            else:
                skipped += 1
        
        return saved, skipped
    
    def mark_as_notified(self, event_id: int, notification_type: str = 'mattermost',
                        success: bool = True, error_message: str = None):
        """
        ทำเครื่องหมายว่า event ถูกส่ง notification แล้ว
        
        Args:
            event_id: Event ID
            notification_type: ประเภทการแจ้งเตือน
            success: สำเร็จหรือไม่
            error_message: ข้อความ error (ถ้ามี)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # อัพเดท events table
                if success:
                    cursor.execute("""
                        UPDATE events 
                        SET notified = 1,
                            notified_at = ?,
                            notification_count = notification_count + 1
                        WHERE event_id = ?
                    """, (datetime.now(timezone.utc).isoformat(), event_id))
                
                # บันทึกใน notification_log
                cursor.execute("""
                    INSERT INTO notification_log 
                    (event_id, event_type, notification_type, sent_at, success, error_message)
                    SELECT event_id, event_type, ?, ?, ?, ?
                    FROM events WHERE event_id = ?
                """, (notification_type, datetime.now(timezone.utc).isoformat(),
                      1 if success else 0, error_message, event_id))
        
        except Exception as e:
            print(f"❌ Error marking event {event_id} as notified: {e}")
    
    def get_unnotified_events(self, limit: int = 100) -> List[Dict]:
        """
        ดึง events ที่ยังไม่ได้ส่ง notification
        
        Args:
            limit: จำนวนสูงสุด
        
        Returns:
            List ของ events
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM events 
                    WHERE notified = 0 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            print(f"❌ Error getting unnotified events: {e}")
            return []
    
    def event_exists(self, event_id: int, event_type: str = None) -> bool:
        """
        เช็คว่า event มีอยู่ใน database หรือไม่
        
        Args:
            event_id: Event ID
            event_type: ประเภท event (optional)
        
        Returns:
            True ถ้ามีอยู่
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if event_type:
                    cursor.execute("""
                        SELECT COUNT(*) FROM events 
                        WHERE event_id = ? AND event_type = ?
                    """, (event_id, event_type))
                else:
                    cursor.execute("""
                        SELECT COUNT(*) FROM events 
                        WHERE event_id = ?
                    """, (event_id,))
                
                return cursor.fetchone()[0] > 0
        
        except Exception as e:
            print(f"❌ Error checking event existence: {e}")
            return False
    
    def save_html_report(self, report_date: str, file_name: str, file_path: str,
                        malicious_count: int, suspicious_count: int,
                        report_url: str = None) -> bool:
        """
        บันทึกข้อมูล HTML report
        
        Args:
            report_date: วันที่รายงาน (YYYY-MM-DD)
            file_name: ชื่อไฟล์
            file_path: path ไปยังไฟล์
            malicious_count: จำนวน malicious events
            suspicious_count: จำนวน suspicious events
            report_url: URL สำหรับเข้าถึงรายงาน
        
        Returns:
            True ถ้าบันทึกสำเร็จ
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                total = malicious_count + suspicious_count
                
                cursor.execute("""
                    INSERT OR REPLACE INTO html_reports (
                        report_date, file_name, file_path,
                        malicious_count, suspicious_count, total_events,
                        generated_at, report_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report_date, file_name, file_path,
                    malicious_count, suspicious_count, total,
                    datetime.now(timezone.utc).isoformat(),
                    report_url
                ))
                
                return True
        
        except Exception as e:
            print(f"❌ Error saving HTML report: {e}")
            return False
    
    def mark_report_sent(self, report_date: str):
        """ทำเครื่องหมายว่ารายงานถูกส่งไป Mattermost แล้ว"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE html_reports 
                    SET sent_to_mattermost = 1,
                        mattermost_sent_at = ?
                    WHERE report_date = ?
                """, (datetime.now(timezone.utc).isoformat(), report_date))
        
        except Exception as e:
            print(f"❌ Error marking report as sent: {e}")
    
    def get_events_by_date(self, date: str, event_type: str = None) -> List[Dict]:
        """
        ดึง events ตามวันที่
        
        Args:
            date: วันที่ (YYYY-MM-DD)
            event_type: ประเภท event (optional)
        
        Returns:
            List ของ events
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if event_type:
                    cursor.execute("""
                        SELECT * FROM events 
                        WHERE DATE(timestamp) = ? AND event_type = ?
                        ORDER BY timestamp DESC
                    """, (date, event_type))
                else:
                    cursor.execute("""
                        SELECT * FROM events 
                        WHERE DATE(timestamp) = ?
                        ORDER BY timestamp DESC
                    """, (date,))
                
                return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            print(f"❌ Error getting events by date: {e}")
            return []
    
    def get_statistics(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        ดึงสถิติ events
        
        Args:
            start_date: วันเริ่มต้น (optional)
            end_date: วันสิ้นสุด (optional)
        
        Returns:
            Dictionary ของสถิติ
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Base query
                where_clause = ""
                params = []
                
                if start_date and end_date:
                    where_clause = "WHERE DATE(timestamp) BETWEEN ? AND ?"
                    params = [start_date, end_date]
                elif start_date:
                    where_clause = "WHERE DATE(timestamp) >= ?"
                    params = [start_date]
                elif end_date:
                    where_clause = "WHERE DATE(timestamp) <= ?"
                    params = [end_date]
                
                # Total events
                cursor.execute(f"""
                    SELECT COUNT(*) FROM events {where_clause}
                """, params)
                total_events = cursor.fetchone()[0]
                
                # By event type
                cursor.execute(f"""
                    SELECT event_type, COUNT(*) 
                    FROM events {where_clause}
                    GROUP BY event_type
                """, params)
                by_type = dict(cursor.fetchall())
                
                # By severity
                cursor.execute(f"""
                    SELECT threat_severity, COUNT(*) 
                    FROM events {where_clause}
                    GROUP BY threat_severity
                """, params)
                by_severity = dict(cursor.fetchall())
                
                # By action
                cursor.execute(f"""
                    SELECT action, COUNT(*) 
                    FROM events {where_clause}
                    GROUP BY action
                """, params)
                by_action = dict(cursor.fetchall())
                
                # Notification stats
                cursor.execute(f"""
                    SELECT 
                        SUM(CASE WHEN notified = 1 THEN 1 ELSE 0 END) as notified,
                        SUM(CASE WHEN notified = 0 THEN 1 ELSE 0 END) as pending
                    FROM events {where_clause}
                """, params)
                notification_stats = cursor.fetchone()
                
                return {
                    'total_events': total_events,
                    'by_type': by_type,
                    'by_severity': by_severity,
                    'by_action': by_action,
                    'notifications': {
                        'notified': notification_stats[0] or 0,
                        'pending': notification_stats[1] or 0
                    }
                }
        
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def cleanup_old_events(self, days: int = 90) -> int:
        """
        ลบ events เก่าที่เกินกำหนด
        
        Args:
            days: จำนวนวันที่จะเก็บไว้
        
        Returns:
            จำนวน events ที่ลบ
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
                
                cursor.execute("""
                    DELETE FROM events 
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                deleted = cursor.rowcount
                
                # Cleanup notification log
                cursor.execute("""
                    DELETE FROM notification_log 
                    WHERE sent_at < ?
                """, (cutoff_date,))
                
                return deleted
        
        except Exception as e:
            print(f"❌ Error cleaning up old events: {e}")
            return 0


# Singleton instance
_db_instance = None

def get_db() -> DatabaseManager:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance


if __name__ == '__main__':
    # Test database
    print("Testing Database Manager...")
    
    db = DatabaseManager('./data/test_events.db')
    
    # Test save event
    test_event = {
        'id': 12345,
        'threat_type': 'MALWARE_VIRUS',
        'threat_severity': 'HIGH',
        'action': 'PREVENTED',
        'status': 'OPEN',
        'description': 'Test malware detected',
        'recorded_device_info': {
            'device_name': 'TEST-PC',
            'hostname': 'test-pc',
            'ip_address': '192.168.1.100',
            'os': 'Windows 10'
        },
        'msp_name': 'Test MSP',
        'tenant_name': 'Test Tenant',
        'file_name': 'malware.exe',
        'path': 'C:\\temp\\malware.exe',
        'file_hash': 'abc123',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    print("✅ Saving test event...")
    result = db.save_event(test_event, 'malicious')
    print(f"   Result: {result}")
    
    print("✅ Checking if event exists...")
    exists = db.event_exists(12345)
    print(f"   Exists: {exists}")
    
    print("✅ Getting statistics...")
    stats = db.get_statistics()
    print(f"   Stats: {stats}")
    
    print("\n✅ Database test completed!")
