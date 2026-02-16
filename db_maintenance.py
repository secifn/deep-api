#!/usr/bin/env python3
"""
Database Maintenance Script
สคริปต์สำหรับบำรุงรักษา database (backup, vacuum, cleanup)
"""

import os
import sys
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from database import get_db


def backup_database(db_path: str, backup_dir: str = None):
    """สำรองข้อมูล database"""
    if backup_dir is None:
        backup_dir = Path(__file__).parent / 'backups'
    else:
        backup_dir = Path(backup_dir)
    
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'events_backup_{timestamp}.db'
    
    print(f"📦 Creating backup...")
    print(f"   Source: {db_path}")
    print(f"   Destination: {backup_file}")
    
    try:
        shutil.copy2(db_path, backup_file)
        
        # Get file size
        size = os.path.getsize(backup_file)
        size_mb = size / (1024 * 1024)
        
        print(f"✅ Backup created successfully!")
        print(f"   Size: {size_mb:.2f} MB")
        
        return str(backup_file)
    
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None


def vacuum_database(db):
    """ทำ VACUUM เพื่อลดขนาด database"""
    print("🗜️  Running VACUUM...")
    
    try:
        with db.get_connection() as conn:
            # Get size before
            cursor = conn.cursor()
            cursor.execute("PRAGMA page_count")
            page_count_before = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            size_before = page_count_before * page_size / (1024 * 1024)
            
            # VACUUM
            conn.execute("VACUUM")
            
            # Get size after
            cursor.execute("PRAGMA page_count")
            page_count_after = cursor.fetchone()[0]
            size_after = page_count_after * page_size / (1024 * 1024)
            
            saved = size_before - size_after
            
            print(f"✅ VACUUM completed!")
            print(f"   Before: {size_before:.2f} MB")
            print(f"   After: {size_after:.2f} MB")
            print(f"   Saved: {saved:.2f} MB ({saved/size_before*100:.1f}%)")
    
    except Exception as e:
        print(f"❌ VACUUM failed: {e}")


def analyze_database(db):
    """วิเคราะห์ database"""
    print("📊 Analyzing database...")
    print()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            size_mb = page_count * page_size / (1024 * 1024)
            
            print(f"Database Size: {size_mb:.2f} MB")
            print()
            
            # Table sizes
            print("Table Statistics:")
            print("-" * 60)
            
            tables = ['events', 'html_reports', 'notification_log']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count:,} rows")
            
            print()
            
            # Events breakdown
            print("Events Breakdown:")
            print("-" * 60)
            
            cursor.execute("""
                SELECT event_type, COUNT(*) 
                FROM events 
                GROUP BY event_type
            """)
            for row in cursor.fetchall():
                print(f"  {row[0]}: {row[1]:,}")
            
            print()
            
            # Notification status
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN notified = 1 THEN 1 ELSE 0 END) as notified,
                    SUM(CASE WHEN notified = 0 THEN 1 ELSE 0 END) as pending
                FROM events
            """)
            notified, pending = cursor.fetchone()
            
            print("Notification Status:")
            print("-" * 60)
            print(f"  Notified: {notified:,}")
            print(f"  Pending: {pending:,}")
            print()
            
            # Date range
            cursor.execute("""
                SELECT MIN(timestamp), MAX(timestamp)
                FROM events
            """)
            min_date, max_date = cursor.fetchone()
            
            if min_date and max_date:
                print("Date Range:")
                print("-" * 60)
                print(f"  Oldest: {min_date[:19]}")
                print(f"  Newest: {max_date[:19]}")
                print()
            
            # Index info
            print("Indexes:")
            print("-" * 60)
            cursor.execute("""
                SELECT name, tbl_name 
                FROM sqlite_master 
                WHERE type = 'index' AND name NOT LIKE 'sqlite_%'
                ORDER BY tbl_name, name
            """)
            for row in cursor.fetchall():
                print(f"  {row[0]} on {row[1]}")
    
    except Exception as e:
        print(f"❌ Analysis failed: {e}")


def cleanup_old_data(db, days: int, dry_run: bool = False):
    """ลบข้อมูลเก่า"""
    print(f"🧹 Cleanup data older than {days} days")
    
    if dry_run:
        print("   (DRY RUN - no actual deletion)")
    
    print()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count events to delete
            from datetime import timedelta, timezone
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT COUNT(*) FROM events WHERE timestamp < ?
            """, (cutoff_date,))
            events_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM notification_log WHERE sent_at < ?
            """, (cutoff_date,))
            logs_count = cursor.fetchone()[0]
            
            print(f"Events to delete: {events_count:,}")
            print(f"Notification logs to delete: {logs_count:,}")
            print()
            
            if events_count == 0 and logs_count == 0:
                print("✅ Nothing to cleanup")
                return
            
            if not dry_run:
                confirm = input("⚠️  Proceed with deletion? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("Cancelled")
                    return
                
                deleted = db.cleanup_old_events(days)
                print(f"✅ Deleted {deleted:,} events")
    
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")


def list_backups(backup_dir: str = None):
    """แสดงรายการ backups"""
    if backup_dir is None:
        backup_dir = Path(__file__).parent / 'backups'
    else:
        backup_dir = Path(backup_dir)
    
    if not backup_dir.exists():
        print("ไม่มี backups")
        return
    
    backups = sorted(backup_dir.glob('events_backup_*.db'), reverse=True)
    
    if not backups:
        print("ไม่มี backups")
        return
    
    print(f"📦 Backups in {backup_dir}")
    print("-" * 80)
    
    for backup in backups:
        size = os.path.getsize(backup)
        size_mb = size / (1024 * 1024)
        mtime = datetime.fromtimestamp(os.path.getmtime(backup))
        
        print(f"  {backup.name}")
        print(f"    Size: {size_mb:.2f} MB")
        print(f"    Date: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Database maintenance tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Backup database
  python db_maintenance.py --backup
  
  # Vacuum database
  python db_maintenance.py --vacuum
  
  # Analyze database
  python db_maintenance.py --analyze
  
  # Cleanup old data (dry run)
  python db_maintenance.py --cleanup 90 --dry-run
  
  # Cleanup old data (actual deletion)
  python db_maintenance.py --cleanup 90
  
  # List backups
  python db_maintenance.py --list-backups
  
  # Full maintenance (backup + vacuum + analyze)
  python db_maintenance.py --full
        """
    )
    
    parser.add_argument('--backup', action='store_true', help='Backup database')
    parser.add_argument('--vacuum', action='store_true', help='Run VACUUM')
    parser.add_argument('--analyze', action='store_true', help='Analyze database')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='Cleanup data older than N days')
    parser.add_argument('--dry-run', action='store_true', help='Dry run for cleanup')
    parser.add_argument('--list-backups', action='store_true', help='List backups')
    parser.add_argument('--full', action='store_true', help='Full maintenance (backup + vacuum + analyze)')
    parser.add_argument('--backup-dir', help='Backup directory (default: ./backups)')
    
    args = parser.parse_args()
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║            Database Maintenance Tool                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Get database
    db = get_db()
    db_path = db.db_path
    
    print(f"Database: {db_path}")
    print()
    
    # Execute commands
    if args.full:
        # Full maintenance
        backup_database(db_path, args.backup_dir)
        print()
        vacuum_database(db)
        print()
        analyze_database(db)
    
    elif args.backup:
        backup_database(db_path, args.backup_dir)
    
    elif args.vacuum:
        vacuum_database(db)
    
    elif args.analyze:
        analyze_database(db)
    
    elif args.cleanup is not None:
        cleanup_old_data(db, args.cleanup, args.dry_run)
    
    elif args.list_backups:
        list_backups(args.backup_dir)
    
    else:
        # Default: analyze
        analyze_database(db)
    
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
