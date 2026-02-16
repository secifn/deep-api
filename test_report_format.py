#!/usr/bin/env python3
"""
Test Daily Report Format - Preview Only (ไม่ส่ง Mattermost)
ทดสอบรูปแบบรายงานก่อนส่งจริง
"""

import os
import sys
from datetime import datetime, timezone, timedelta, date
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv('/home/api/deep-api/.env')

# Bangkok timezone
TZ_BANGKOK = timezone(timedelta(hours=7))

def build_mattermost_message_preview(malicious_count, suspicious_count, detected_count, prevented_count, severity_counts, report_date=None):
    """สร้างข้อความสำหรับ Mattermost แบบตาราง (Preview)"""
    
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
    total_events = malicious_count + suspicious_count
    
    # สร้าง message แบบตาราง (เหมือนในรูป)
    message = f"""### 🔒 Deep Instinct Security Report

**วันที่:** {date_str} | **เวลา:** {time_str} (GMT+7)

---

#### 📊 สรุป Events วันที่ {date_display}

| หมวดหมู่ | จำนวน |
|:---------|------:|
| 🔴 Malicious | {malicious_count} |
| 🟡 Suspicious | {suspicious_count} |
| **รวมทั้งหมด** | **{total_events}** |

---

#### 🛡️ การดำเนินการ (Actions)

| Action | จำนวน |
|:-------|------:|
| 👁️ DETECTED | {detected_count} |
| 🛡️ PREVENTED | {prevented_count} |

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
        if severity in severity_counts and severity_counts[severity] > 0:
            if not has_severity:
                has_severity = True
            message += f"| {severity_display[severity]} | {severity_counts[severity]} |\n"
    
    if not has_severity:
        message += "| ไม่มีข้อมูล | 0 |\n"
    
    message += "\n---\n\n"
    message += "📄 [ดูรายละเอียด Events ทั้งหมด](https://allevent.ifn-dtc.online/event_detail/event_details_YYYY-MM-DD.html)\n\n"
    message += "🔗 [Deep Instinct Dashboard](https://ro.customers.deepinstinctweb.com)\n"
    
    return message


def main():
    """Main function - Preview only"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   Deep Instinct Report Preview (ไม่ส่ง Mattermost)         ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # ตัวอย่างข้อมูลจากรูป
    print("📝 ตัวอย่างที่ 1: ข้อมูลจากรูปที่ให้มา")
    print("=" * 70)
    
    # ข้อมูลตามรูป
    report_date = date(2026, 2, 15)  # 15/02/2026
    malicious = 0
    suspicious = 10
    detected = 5
    prevented = 5
    severity = {
        'MODERATE': 3,
        'LOW': 7
    }
    
    message1 = build_mattermost_message_preview(
        malicious, suspicious, detected, prevented, severity, report_date
    )
    print(message1)
    
    print("\n" + "=" * 70)
    print()
    
    # ตัวอย่างที่ 2
    print("📝 ตัวอย่างที่ 2: ข้อมูลหลากหลาย")
    print("=" * 70)
    
    report_date2 = date(2026, 2, 16)
    malicious2 = 25
    suspicious2 = 15
    detected2 = 30
    prevented2 = 10
    severity2 = {
        'CRITICAL': 2,
        'VERY_HIGH': 3,
        'HIGH': 8,
        'MODERATE': 15,
        'LOW': 12
    }
    
    message2 = build_mattermost_message_preview(
        malicious2, suspicious2, detected2, prevented2, severity2, report_date2
    )
    print(message2)
    
    print("\n" + "=" * 70)
    print()
    
    # ตัวอย่างที่ 3 - วันนี้
    print("📝 ตัวอย่างที่ 3: รายงานวันนี้")
    print("=" * 70)
    
    malicious3 = 5
    suspicious3 = 3
    detected3 = 6
    prevented3 = 2
    severity3 = {
        'HIGH': 2,
        'MODERATE': 4,
        'LOW': 2
    }
    
    message3 = build_mattermost_message_preview(
        malicious3, suspicious3, detected3, prevented3, severity3, None
    )
    print(message3)
    
    print("\n" + "=" * 70)
    print()
    print("✅ Preview เสร็จสิ้น!")
    print()
    print("💡 Tips:")
    print("   - รูปแบบตารางจะแสดงสวยงามใน Mattermost")
    print("   - วันที่แสดงเป็น พ.ศ. (เช่น 15/02/2569)")
    print("   - แสดงเฉพาะ Severity ที่มีค่ามากกว่า 0")
    print("   - รูปแบบเหมือนในรูปที่ให้มา")
    print()
    print("🚀 พร้อมใช้งานจริงแล้ว!")


if __name__ == "__main__":
    main()
