#!/usr/bin/env python3
"""
สร้างหน้า index สำหรับรายงาน Deep Instinct - ใช้ดูย้อนหลัง
แบ่งเป็นหัวข้อ: Daily-report และ เครื่องที่ไม่อยู่ใน Snipe-IT
กดที่หัวข้อเพื่อแสดงรายการเลือกดูแต่ละวัน
"""

import os
import re
import glob


def _collect_dates_from_pattern(event_detail_dir, pattern, regex):
    """สแกนไฟล์ตาม pattern แล้ว extract วันที่"""
    files = glob.glob(os.path.join(event_detail_dir, pattern))
    dates = set()
    for f in files:
        m = re.search(regex, os.path.basename(f))
        if m:
            dates.add(m.group(1))
    return sorted(dates, reverse=True)


def build_reports_index(event_detail_dir):
    """
    สร้างไฟล์ index.html ใน event_detail/ แสดงรายการรายงาน
    แบ่งเป็น 2 หัวข้อ: Daily-report, เครื่องที่ไม่อยู่ใน Snipe-IT
    """
    event_detail_dir = os.path.abspath(event_detail_dir)
    os.makedirs(event_detail_dir, exist_ok=True)

    # 1. Daily-report: event_details_*.html และ *-daily-report.md
    daily_dates = _collect_dates_from_pattern(
        event_detail_dir, "event_details_*.html",
        r"event_details_(\d{4}-\d{2}-\d{2})\.html$"
    )
    daily_rows = ""
    for d in daily_dates:
        html_file = f"event_details_{d}.html"
        md_file = f"{d}-daily-report.md"
        md_path = os.path.join(event_detail_dir, md_file)
        has_md = os.path.exists(md_path)
        md_btn = f'<a href="{md_file}" class="btn btn-raw" target="_blank">Raw MD</a>' if has_md else '<span class="btn btn-disabled">Raw MD</span>'
        daily_rows += f"""
        <tr>
            <td><span class="file-icon">📄</span><span class="report-name">{d}-daily-report</span></td>
            <td class="actions">
                <a href="{html_file}" class="btn btn-view" target="_blank">View HTML</a>
                {md_btn}
            </td>
        </tr>"""

    # 2. เครื่องที่ไม่อยู่ใน Snipe-IT: not_found_devices_*.html
    notfound_dates = _collect_dates_from_pattern(
        event_detail_dir, "not_found_devices_*.html",
        r"not_found_devices_(\d{4}-\d{2}-\d{2})\.html$"
    )
    notfound_rows = ""
    for d in notfound_dates:
        html_file = f"not_found_devices_{d}.html"
        notfound_rows += f"""
        <tr>
            <td><span class="file-icon">⚠️</span><span class="report-name">{d} - เครื่องที่ไม่อยู่ใน Snipe-IT</span></td>
            <td class="actions">
                <a href="{html_file}" class="btn btn-view" target="_blank">View HTML</a>
            </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deep Instinct Security Reports</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1d21;
            color: #e4e6eb;
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{
            display: flex; align-items: center; gap: 12px;
            font-size: 28px; margin-bottom: 30px; color: #6ab2ff;
        }}
        h1 .shield {{ font-size: 32px; }}
        .section {{
            margin-bottom: 24px;
            background: #242628;
            border-radius: 8px;
            overflow: hidden;
        }}
        .section summary {{
            padding: 16px 20px;
            font-size: 18px;
            font-weight: 600;
            color: #6ab2ff;
            cursor: pointer;
            list-style: none;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section summary::-webkit-details-marker {{ display: none; }}
        .section summary::before {{ content: "▶"; font-size: 12px; transition: transform 0.2s; }}
        .section[open] summary::before {{ transform: rotate(90deg); }}
        .section-content {{ padding: 0 20px 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        tr {{ border-bottom: 1px solid #3a3d42; }}
        tr:last-child {{ border-bottom: none; }}
        tr:hover {{ background: #2d3035; }}
        td {{ padding: 12px 16px; }}
        .report-name {{ font-size: 15px; }}
        .file-icon {{ margin-right: 10px; opacity: 0.8; }}
        .actions {{ text-align: right; }}
        .btn {{
            display: inline-block;
            padding: 8px 16px;
            margin-left: 8px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
        }}
        .btn-view, .btn-raw {{ background: #4a9eff; color: white; border: none; }}
        .btn-view:hover, .btn-raw:hover {{ background: #6ab2ff; }}
        .btn-disabled {{ background: #3a3d42; color: #6c757d; cursor: not-allowed; }}
    </style>
</head>
<body>
    <div class="container">
        <h1><span class="shield">🛡️</span> Deep Instinct Security Reports</h1>

        <details class="section" open>
            <summary>📅 Daily-report</summary>
            <div class="section-content">
                <table>
                    <tbody>{daily_rows}
                    </tbody>
                </table>
            </div>
        </details>

        <details class="section">
            <summary>⚠️ เครื่องที่ไม่อยู่ใน Snipe-IT</summary>
            <div class="section-content">
                <table>
                    <tbody>{notfound_rows}
                    </tbody>
                </table>
            </div>
        </details>
    </div>
</body>
</html>"""

    index_path = os.path.join(event_detail_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    return index_path
