#!/usr/bin/env python3
"""
ดึงรายการ Device (Hardware) และผู้รับผิดชอบจาก Snip IT / IT Parcel API
ใช้ .env1: IT_PARCEL_API_URL, IT_PARCEL_TOKEN
รองรับการค้นหาตามชื่อเครื่องและผู้รับผิดชอบ
"""
import os
import sys
import json
import argparse
import requests
from pathlib import Path

# โหลด .env1
env_path = Path(__file__).resolve().parent / ".env1"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

BASE_URL = os.environ.get("IT_PARCEL_API_URL", "").rstrip("/")
TOKEN = os.environ.get("IT_PARCEL_TOKEN", "")

if not BASE_URL or not TOKEN:
    print("กรุณาตั้งค่า IT_PARCEL_API_URL และ IT_PARCEL_TOKEN ใน .env1", file=sys.stderr)
    sys.exit(1)


def get_name(row):
    return (
        row.get("name")
        or row.get("asset_tag")
        or row.get("hostname")
        or row.get("device_name")
        or "-"
    )


def get_responsible(row):
    assigned = row.get("assigned_to")
    if assigned is None:
        return "-"
    if isinstance(assigned, dict):
        return (
            assigned.get("name")
            or assigned.get("username")
            or assigned.get("display_name")
            or str(assigned.get("id", ""))
        )
    return str(assigned)


def match_keyword(text, keyword):
    """เช็คว่า keyword อยู่ใน text หรือไม่ (ไม่สนใจตัวพิมพ์เล็ก-ใหญ่)"""
    if not keyword or not text:
        return True
    return keyword.lower() in str(text).lower()


def main():
    parser = argparse.ArgumentParser(
        description="ดึงรายการ Device และผู้รับผิดชอบจาก Snip IT (ค้นหาตามชื่อเครื่อง/ผู้รับผิดชอบได้)"
    )
    parser.add_argument(
        "-n", "--name",
        metavar="คำค้น",
        help="ค้นหาตามชื่อเครื่อง / asset / hostname (รองรับคำย่อ)",
    )
    parser.add_argument(
        "-r", "--responsible",
        metavar="คำค้น",
        help="ค้นหาตามผู้รับผิดชอบ (ชื่อคนหรือหน่วย)",
    )
    args = parser.parse_args()

    url = f"{BASE_URL}/hardware"
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}
    params = {"limit": 500}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        print(f"เชื่อมต่อ API ไม่ได้: {e}", file=sys.stderr)
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}", file=sys.stderr)
            print(e.response.text[:500], file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ตอบกลับไม่ใช่ JSON: {e}", file=sys.stderr)
        sys.exit(1)

    rows = data.get("rows") or data.get("data") or []
    if not rows and isinstance(data, list):
        rows = data

    if not rows:
        print("ไม่มีข้อมูล hardware ในระบบ (หรือ API ส่งรูปแบบอื่น)")
        print("Response keys:", list(data.keys()) if isinstance(data, dict) else "list")
        return

    # กรองตามคำค้น (ชื่อเครื่อง และ/หรือ ผู้รับผิดชอบ)
    if args.name or args.responsible:
        filtered = []
        for row in rows:
            name = get_name(row)
            resp = get_responsible(row)
            ok_name = match_keyword(name, args.name)
            ok_resp = match_keyword(resp, args.responsible)
            if ok_name and ok_resp:
                filtered.append(row)
        rows = filtered
        if args.name:
            print(f"ค้นหา 'ชื่อเครื่อง' มีคำว่า: {args.name}")
        if args.responsible:
            print(f"ค้นหา 'ผู้รับผิดชอบ' มีคำว่า: {args.responsible}")
        print(f"พบ {len(rows)} รายการ\n")
    else:
        print(f"พบ {len(rows)} รายการ\n")

    print("-" * 80)
    print(f"{'ลำดับ':<6} {'ชื่อเครื่อง / Asset':<35} {'ผู้รับผิดชอบ':<30}")
    print("-" * 80)

    for i, row in enumerate(rows, 1):
        name = get_name(row)
        responsible = get_responsible(row)
        name_str = str(name)[:34]
        resp_str = str(responsible)[:29]
        print(f"{i:<6} {name_str:<35} {resp_str:<30}")

    print("-" * 80)


if __name__ == "__main__":
    main()
