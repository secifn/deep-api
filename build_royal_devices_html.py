#!/usr/bin/env python3
"""
สร้างไฟล์ HTML สำหรับเครื่องของโครงการส่วนพระองค์ (Royal Chitralada Projects)
แยกตาม Action: DETECTED และ PREVENTED (ไฟล์คนละไฟล์)
"""

import os
from datetime import datetime, timezone, timedelta

TZ_BANGKOK = timezone(timedelta(hours=7))


def _render_device_card(device_name, events, action_class):
    """ helper สร้าง HTML card สำหรับแต่ละเครื่อง """
    if not events:
        return ""
    first = events[0]
    rec = first.get('recorded_device_info', {})
    ip = rec.get('ip_address', 'N/A')
    os_info = rec.get('os', 'N/A')
    tenant = first.get('tenant_name', 'N/A')
    mal_count = sum(1 for e in events if e.get('_event_type') == 'malicious')
    sus_count = sum(1 for e in events if e.get('_event_type') == 'suspicious')
    type_badges = []
    if mal_count:
        type_badges.append('<span class="badge malicious">Malicious ({})</span>'.format(mal_count))
    if sus_count:
        type_badges.append('<span class="badge suspicious">Suspicious ({})</span>'.format(sus_count))
    type_html = ' '.join(type_badges) if type_badges else '<span class="badge suspicious">-</span>'

    card = f"""
            <div class="device-card {action_class}">
                <div class="device-header">🖥️ {device_name}</div>
                <div class="detail-row">
                    <div class="detail-label">IP Address:</div>
                    <div class="detail-value">{ip}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">OS:</div>
                    <div class="detail-value">{os_info}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Tenant:</div>
                    <div class="detail-value">{tenant}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">ประเภท Events:</div>
                    <div class="detail-value">{type_html}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">จำนวนเหตุการณ์:</div>
                    <div class="detail-value">{len(events)}</div>
                </div>
                <div class="event-list">
                    <div class="detail-label" style="margin-bottom:8px;">รายการ Events:</div>
"""
    for ev in sorted(events, key=lambda x: x.get('_bangkok_time') or '', reverse=True):
        dt = ev.get('_bangkok_time')
        time_str = dt.strftime('%d/%m/%Y %H:%M') if dt else 'N/A'
        severity = ev.get('threat_severity', 'N/A')
        sev_cls = severity.lower().replace('_', '-') if severity and severity != 'N/A' else 'moderate'
        threat_type = ev.get('threat_type', 'N/A')
        ev_id = ev.get('id', 'N/A')
        desc = (ev.get('description') or '')[:80] + ('...' if len(ev.get('description', '') or '') > 80 else '')
        card += f"""
                    <div class="event-item">
                        <span class="badge severity-{sev_cls}">{severity}</span>
                        Event #{ev_id} | {time_str} | {threat_type}
                        <br><span style="color:#666;font-size:12px;">{desc}</span>
                    </div>
"""
    card += """
                </div>
            </div>
"""
    return card


def _build_single_action_html(device_list, report_date_str, date_str, action_class, title):
    """ สร้าง HTML หน้าเดียวเฉพาะ action นั้น (DETECTED หรือ PREVENTED เท่านั้น) """
    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>เครื่องโครงการส่วนพระองค์ - {title} - Deep Instinct</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 16px; }}
        .content {{ padding: 30px; }}
        .section h2 {{ color: #333; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #667eea; font-size: 22px; }}
        .section h2.detected {{ border-bottom-color: #3498db; }}
        .section h2.prevented {{ border-bottom-color: #e74c3c; }}
        .device-card {{ background: #f9f9f9; border-left: 4px solid #667eea; padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
        .device-card.detected {{ border-left-color: #3498db; }}
        .device-card.prevented {{ border-left-color: #e74c3c; }}
        .device-header {{ font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #e0e0e0; }}
        .detail-row {{ display: grid; grid-template-columns: 180px 1fr; gap: 10px; padding: 6px 0; border-bottom: 1px solid #f0f0f0; font-size: 14px; }}
        .detail-label {{ font-weight: 600; color: #555; }}
        .detail-value {{ color: #333; word-break: break-all; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; margin-right: 5px; margin-bottom: 5px; }}
        .badge.malicious {{ background: #e74c3c; color: white; }}
        .badge.suspicious {{ background: #f39c12; color: white; }}
        .badge.severity-moderate {{ background: #f39c12; color: white; }}
        .badge.severity-low {{ background: #27ae60; color: white; }}
        .badge.severity-high {{ background: #e67e22; color: white; }}
        .badge.severity-very-high {{ background: #e74c3c; color: white; }}
        .event-list {{ margin-top: 15px; padding-top: 10px; border-top: 1px dashed #ddd; }}
        .event-item {{ padding: 8px 0; border-bottom: 1px solid #eee; font-size: 13px; }}
        .event-item:last-child {{ border-bottom: none; }}
        .no-data {{ text-align: center; padding: 30px; color: #6c757d; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👑 เครื่องโครงการส่วนพระองค์ (Royal Chitralada Projects) - {title}</h1>
            <p>รายละเอียดเครื่องที่เกิดเหตุการณ์ {title} เท่านั้น</p>
            <p>วันที่รายงาน: {report_date_str} | สร้างเมื่อ: {date_str} (GMT+7)</p>
        </div>
        <div class="content">
            <div class="section">
                <h2 class="{action_class}">{title} - จำนวน {len(device_list)} เครื่อง</h2>
"""
    if device_list:
        for device_name, events in sorted(device_list, key=lambda x: x[0]):
            html += _render_device_card(device_name, events, action_class)
    else:
        html += '                <div class="no-data">ไม่มีเครื่องในหมวดนี้</div>\n'

    html += """
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html


def build_royal_devices_html(royal_detected, royal_prevented, output_dir, date_filename, report_date=None):
    """
    สร้างไฟล์ HTML แยก 2 ไฟล์: DETECTED เท่านั้น และ PREVENTED เท่านั้น
    royal_detected: list of (device_name, [events])
    royal_prevented: list of (device_name, [events])
    Returns: (detected_filename, prevented_filename)
    """
    now_bangkok = datetime.now(TZ_BANGKOK)
    date_str = now_bangkok.strftime('%d/%m/%Y %H:%M:%S')
    report_date_str = report_date.strftime('%d/%m/%Y') if report_date else date_str.split()[0]

    # ไฟล์ DETECTED
    detected_filename = f"royal_devices_detected_{date_filename}.html"
    detected_path = os.path.join(output_dir, detected_filename)
    html_detected = _build_single_action_html(
        royal_detected, report_date_str, date_str, 'detected', 'DETECTED'
    )
    with open(detected_path, 'w', encoding='utf-8') as f:
        f.write(html_detected)

    # ไฟล์ PREVENTED
    prevented_filename = f"royal_devices_prevented_{date_filename}.html"
    prevented_path = os.path.join(output_dir, prevented_filename)
    html_prevented = _build_single_action_html(
        royal_prevented, report_date_str, date_str, 'prevented', 'PREVENTED'
    )
    with open(prevented_path, 'w', encoding='utf-8') as f:
        f.write(html_prevented)

    return detected_filename, prevented_filename
