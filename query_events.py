#!/usr/bin/env python3
"""
Query Events from Database
สคริปต์สำหรับ query และดูข้อมูล events จาก database
"""

import sys
import argparse
from datetime import datetime, timedelta, date
from database import get_db
from tabulate import tabulate


def query_events_by_date(db, target_date, event_type=None):
    """Query events ตามวันที่"""
    print(f"\n📅 Events for {target_date}")
    print("=" * 80)
    
    events = db.get_events_by_date(target_date, event_type)
    
    if not events:
        print("ไม่พบ events")
        return
    
    print(f"พบ {len(events)} events\n")
    
    # แสดงตาราง
    table_data = []
    for event in events[:50]:  # แสดงแค่ 50 รายการแรก
        table_data.append([
            event['event_id'],
            event['event_type'],
            event['threat_severity'] or 'N/A',
            event['action'] or 'N/A',
            event['device_name'] or 'N/A',
            '✅' if event['notified'] else '❌',
            event['timestamp'][:19] if event['timestamp'] else 'N/A'
        ])
    
    headers = ['ID', 'Type', 'Severity', 'Action', 'Device', 'Notified', 'Timestamp']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    if len(events) > 50:
        print(f"\n... และอีก {len(events) - 50} events")


def show_statistics(db, start_date=None, end_date=None):
    """แสดงสถิติ"""
    print("\n📊 Statistics")
    print("=" * 80)
    
    if start_date and end_date:
        print(f"Period: {start_date} to {end_date}\n")
    elif start_date:
        print(f"From: {start_date}\n")
    elif end_date:
        print(f"Until: {end_date}\n")
    else:
        print("All time\n")
    
    stats = db.get_statistics(start_date, end_date)
    
    print(f"Total Events: {stats.get('total_events', 0)}")
    print()
    
    # By Type
    print("By Type:")
    by_type = stats.get('by_type', {})
    for event_type, count in by_type.items():
        print(f"  {event_type}: {count}")
    print()
    
    # By Severity
    print("By Severity:")
    by_severity = stats.get('by_severity', {})
    severity_order = ['CRITICAL', 'VERY_HIGH', 'HIGH', 'MODERATE', 'LOW', 'VERY_LOW', 'N/A', None]
    for severity in severity_order:
        if severity in by_severity:
            print(f"  {severity or 'Unknown'}: {by_severity[severity]}")
    print()
    
    # By Action
    print("By Action:")
    by_action = stats.get('by_action', {})
    for action, count in by_action.items():
        print(f"  {action or 'Unknown'}: {count}")
    print()
    
    # Notifications
    notifications = stats.get('notifications', {})
    print("Notifications:")
    print(f"  Notified: {notifications.get('notified', 0)}")
    print(f"  Pending: {notifications.get('pending', 0)}")


def show_unnotified(db, limit=50):
    """แสดง events ที่ยังไม่ได้ส่ง notification"""
    print(f"\n🔔 Unnotified Events (limit: {limit})")
    print("=" * 80)
    
    events = db.get_unnotified_events(limit)
    
    if not events:
        print("✅ ไม่มี events ที่รอส่ง notification")
        return
    
    print(f"พบ {len(events)} events ที่ยังไม่ได้ส่ง\n")
    
    table_data = []
    for event in events:
        table_data.append([
            event['event_id'],
            event['event_type'],
            event['threat_severity'] or 'N/A',
            event['device_name'] or 'N/A',
            event['timestamp'][:19] if event['timestamp'] else 'N/A'
        ])
    
    headers = ['ID', 'Type', 'Severity', 'Device', 'Timestamp']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def show_reports(db):
    """แสดงรายการ HTML reports"""
    print("\n📄 HTML Reports")
    print("=" * 80)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT report_date, file_name, malicious_count, suspicious_count, 
                   total_events, sent_to_mattermost, generated_at
            FROM html_reports
            ORDER BY report_date DESC
            LIMIT 30
        """)
        
        reports = cursor.fetchall()
    
    if not reports:
        print("ไม่มีรายงาน")
        return
    
    print(f"พบ {len(reports)} รายงาน\n")
    
    table_data = []
    for report in reports:
        table_data.append([
            report[0],  # date
            report[2],  # malicious
            report[3],  # suspicious
            report[4],  # total
            '✅' if report[5] else '❌',  # sent
            report[6][:19] if report[6] else 'N/A'  # generated_at
        ])
    
    headers = ['Date', 'Malicious', 'Suspicious', 'Total', 'Sent', 'Generated']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def search_events(db, keyword, limit=50):
    """ค้นหา events"""
    print(f"\n🔍 Search: '{keyword}' (limit: {limit})")
    print("=" * 80)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Search in multiple fields
        cursor.execute("""
            SELECT event_id, event_type, threat_severity, device_name, 
                   file_name, description, timestamp, notified
            FROM events
            WHERE device_name LIKE ? 
               OR file_name LIKE ?
               OR description LIKE ?
               OR file_path LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
        
        results = cursor.fetchall()
    
    if not results:
        print("ไม่พบผลลัพธ์")
        return
    
    print(f"พบ {len(results)} events\n")
    
    table_data = []
    for event in results:
        table_data.append([
            event[0],  # event_id
            event[1],  # event_type
            event[2] or 'N/A',  # severity
            event[3] or 'N/A',  # device_name
            event[4][:30] if event[4] else 'N/A',  # file_name
            '✅' if event[7] else '❌',  # notified
            event[6][:19] if event[6] else 'N/A'  # timestamp
        ])
    
    headers = ['ID', 'Type', 'Severity', 'Device', 'File', 'Notified', 'Timestamp']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def cleanup_old_events(db, days):
    """ลบ events เก่า"""
    print(f"\n🧹 Cleanup events older than {days} days")
    print("=" * 80)
    
    confirm = input(f"⚠️  คุณแน่ใจหรือไม่? (yes/no): ")
    if confirm.lower() != 'yes':
        print("ยกเลิก")
        return
    
    deleted = db.cleanup_old_events(days)
    print(f"✅ ลบ {deleted} events")


def main():
    parser = argparse.ArgumentParser(
        description='Query events from database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # แสดงสถิติทั้งหมด
  python query_events.py --stats
  
  # Query events วันนี้
  python query_events.py --date today
  
  # Query events วันที่กำหนด
  python query_events.py --date 2026-02-13
  
  # แสดง events ที่ยังไม่ได้ส่ง notification
  python query_events.py --unnotified
  
  # แสดงรายการ HTML reports
  python query_events.py --reports
  
  # ค้นหา events
  python query_events.py --search "malware"
  
  # ลบ events เก่ากว่า 90 วัน
  python query_events.py --cleanup 90
        """
    )
    
    parser.add_argument('--date', help='Query events by date (YYYY-MM-DD or "today" or "yesterday")')
    parser.add_argument('--type', choices=['malicious', 'suspicious'], help='Filter by event type')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--start-date', help='Start date for statistics (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date for statistics (YYYY-MM-DD)')
    parser.add_argument('--unnotified', action='store_true', help='Show unnotified events')
    parser.add_argument('--reports', action='store_true', help='Show HTML reports')
    parser.add_argument('--search', help='Search events by keyword')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='Cleanup events older than N days')
    parser.add_argument('--limit', type=int, default=50, help='Limit results (default: 50)')
    
    args = parser.parse_args()
    
    # Initialize database
    db = get_db()
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║              Deep Instinct Events Query Tool                ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # Execute commands
    if args.date:
        # Parse date
        if args.date.lower() == 'today':
            target_date = date.today().strftime('%Y-%m-%d')
        elif args.date.lower() == 'yesterday':
            target_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            target_date = args.date
        
        query_events_by_date(db, target_date, args.type)
    
    elif args.stats:
        show_statistics(db, args.start_date, args.end_date)
    
    elif args.unnotified:
        show_unnotified(db, args.limit)
    
    elif args.reports:
        show_reports(db)
    
    elif args.search:
        search_events(db, args.search, args.limit)
    
    elif args.cleanup:
        cleanup_old_events(db, args.cleanup)
    
    else:
        # Default: show today's stats
        today = date.today().strftime('%Y-%m-%d')
        show_statistics(db, today, today)
        query_events_by_date(db, today)
    
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
