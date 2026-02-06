#!/bin/bash
# สคริปต์สำหรับติดตั้ง systemd service

set -e

if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root"
    echo "   Please run: sudo ./install_service.sh"
    exit 1
fi

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       Install Deep Instinct Monitor as systemd service       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ตัวแปร
SERVICE_NAME="deepinstinct-monitor"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/deepinstinct_to_mattermost.py"
PYTHON_PATH=$(which python3)
CURRENT_USER=$(logname)

echo "📁 Script directory: $SCRIPT_DIR"
echo "🐍 Python path: $PYTHON_PATH"
echo "👤 Running as user: $CURRENT_USER"
echo ""

# ตรวจสอบว่าไฟล์สคริปต์มีอยู่
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

# สร้างไฟล์ service
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "📝 Creating systemd service file at $SERVICE_FILE..."

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Deep Instinct to Mattermost Monitor
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=$PYTHON_PATH $SCRIPT_PATH
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created"
echo ""

# Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

# Enable service
echo "🔧 Enabling service..."
systemctl enable "$SERVICE_NAME"

# Start service
echo "🚀 Starting service..."
systemctl start "$SERVICE_NAME"

echo ""
echo "✅ Service installed and started successfully!"
echo ""
echo "Useful commands:"
echo "  Check status:    sudo systemctl status $SERVICE_NAME"
echo "  View logs:       sudo journalctl -u $SERVICE_NAME -f"
echo "  Stop service:    sudo systemctl stop $SERVICE_NAME"
echo "  Start service:   sudo systemctl start $SERVICE_NAME"
echo "  Restart service: sudo systemctl restart $SERVICE_NAME"
echo "  Disable service: sudo systemctl disable $SERVICE_NAME"
echo ""

# แสดง status
echo "Current status:"
systemctl status "$SERVICE_NAME" --no-pager
