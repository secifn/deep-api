#!/usr/bin/env python3
"""
สร้างไฟล์ HTML สำหรับเครื่องที่ไม่พบใน Snipe IT
"""

from datetime import datetime, timezone, timedelta

TZ_BANGKOK = timezone(timedelta(hours=7))


def build_not_found_devices_html(devices_not_found, output_file):
    """สร้างไฟล์ HTML สำหรับเครื่องที่ไม่พบใน Snipe IT"""
    
    now_bangkok = datetime.now(TZ_BANGKOK)
    date_str = now_bangkok.strftime('%d/%m/%Y %H:%M:%S')
    
    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>เครื่องที่ไม่พบใน Snipe IT - Deep Instinct</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 16px; }}
        .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 30px; border-radius: 5px; }}
        .alert-title {{ font-weight: bold; color: #856404; margin-bottom: 5px; }}
        .alert-text {{ color: #856404; }}
        .content {{ padding: 30px; }}
        .summary {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
        .summary h2 {{ color: #e74c3c; margin-bottom: 15px; }}
        .table-container {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        thead {{ background: #e74c3c; color: white; }}
        th {{ padding: 15px; text-align: left; font-weight: 600; }}
        td {{ padding: 12px 15px; border-bottom: 1px solid #dee2e6; }}
        tbody tr:hover {{ background: #f8f9fa; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
        .badge.malicious {{ background: #e74c3c; color: white; }}
        .badge.suspicious {{ background: #f39c12; color: white; }}
        .no-data {{ text-align: center; padding: 40px; color: #6c757d; }}
        .footer {{ padding: 20px 30px; background: #f8f9fa; border-radius: 0 0 10px 10px; text-align: center; color: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ เครื่องที่ไม่พบใน Snipe IT</h1>
            <p>รายการเครื่องที่ตรวจพบ Events แต่ไม่พบข้อมูลใน Snipe IT</p>
            <p>สร้างเมื่อ: {date_str} (GMT+7)</p>
        </div>
        
        <div class="alert">
            <div class="alert-title">⚠️ คำเตือน</div>
            <div class="alert-text">เครื่องเหล่านี้ไม่พบข้อมูลใน Snipe IT ทำให้ไม่สามารถระบุผู้รับผิดชอบได้ กรุณาตรวจสอบและเพิ่มข้อมูลเข้า Snipe IT</div>
        </div>
        
        <div class="content">
            <div class="summary">
                <h2>📊 สรุป</h2>
                <p style="font-size: 18px; color: #e74c3c; font-weight: bold;">จำนวนเครื่องที่ไม่พบ: {len(devices_not_found)} เครื่อง</p>
            </div>
"""
    
    if devices_not_found:
        html += """
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>ลำดับ</th>
                            <th>Hostname</th>
                            <th>IP Address</th>
                            <th>Operating System</th>
                            <th>Event Type</th>
                            <th>Event ID</th>
                            <th>เวลาล่าสุด</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        for idx, device in enumerate(devices_not_found, 1):
            timestamp = device.get('timestamp')
            time_str = timestamp.strftime('%d/%m/%Y %H:%M:%S') if timestamp else 'N/A'
            event_type = device.get('event_type', 'N/A')
            badge_class = 'malicious' if event_type == 'malicious' else 'suspicious'
            
            html += f"""
                        <tr>
                            <td>{idx}</td>
                            <td><strong>{device.get('hostname', 'N/A')}</strong></td>
                            <td>{device.get('ip_address', 'N/A')}</td>
                            <td>{device.get('os', 'N/A')}</td>
                            <td><span class="badge {badge_class}">{event_type.upper()}</span></td>
                            <td>{device.get('event_id', 'N/A')}</td>
                            <td>{time_str}</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
"""
    else:
        html += """
            <div class="no-data">
                <p style="font-size: 18px;">✅ ไม่พบเครื่องที่ไม่อยู่ใน Snipe IT</p>
                <p>เครื่องทั้งหมดมีข้อมูลใน Snipe IT ครบถ้วน</p>
            </div>
"""
    
    html += f"""
        </div>
        
        <div class="footer">
            <p>รายงานนี้สร้างโดยระบบอัตโนมัติจาก Deep Instinct Security Report</p>
            <p>จำนวนเครื่องทั้งหมด: {len(devices_not_found)} เครื่อง</p>
        </div>
    </div>
</body>
</html>
"""
    
    # บันทึกไฟล์
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_file, len(devices_not_found)
