#!/bin/bash
# Deep Instinct Daily Report - ดึงข้อมูลย้อนหลัง 1 วัน
# ใช้กับ cron: รันทุกวัน 07:00

cd /home/api/DeepInstint

# คำนวณวันที่เมื่อวาน (ย้อนหลัง 1 วัน)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)

# รันสคริปต์ส่งรายงานพร้อมวันที่เมื่อวาน
/usr/bin/python3 send_today_to_mattermost.py "$YESTERDAY"
