#!/bin/bash
# Setup script สำหรับติดตั้งและตั้งค่า Deep Instinct to Mattermost Integration

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   Deep Instinct to Mattermost Integration - Setup Script    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ตรวจสอบว่ามี Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Please install Python 3 first:"
    echo "   sudo apt-get update && sudo apt-get install python3 python3-pip"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# ตรวจสอบว่ามี pip
if ! command -v pip3 &> /dev/null; then
    echo "⚠️  Warning: pip3 is not found, installing..."
    sudo apt-get update && sudo apt-get install -y python3-pip
fi

echo "✅ pip3 found: $(pip3 --version)"
echo ""

# ติดตั้ง dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

# ตรวจสอบไฟล์ .env1
if [ ! -f ".env1" ]; then
    echo "⚠️  Warning: .env1 not found, creating from template..."
    cp .env.example .env1
    echo "✅ Created .env1 from template"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env1 and add your credentials:"
    echo "   - DEEPINSTINCT_URL"
    echo "   - TOKENS_KEY"
    echo "   - MATTERMOST_WEBHOOK_URL"
    echo ""
    exit 0
fi

# ตรวจสอบว่า .env1 มีค่าที่จำเป็น
echo "🔍 Checking .env1 configuration..."

if grep -q "your-mattermost-server.com" .env1 || grep -q "xxx-your-hook-id-xxx" .env1; then
    echo "⚠️  Warning: MATTERMOST_WEBHOOK_URL appears to be a placeholder"
    echo "   Please update .env1 with your actual Mattermost webhook URL"
    echo ""
fi

# ทดสอบการเชื่อมต่อ
echo "🧪 Testing connections..."
python3 test_connection.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Run one-time fetch to test:"
    echo "     python3 fetch_events_once.py --dry-run"
    echo ""
    echo "  2. Run continuous monitoring:"
    echo "     python3 deepinstinct_to_mattermost.py"
    echo ""
    echo "  3. (Optional) Install as systemd service:"
    echo "     sudo ./install_service.sh"
    echo ""
else
    echo ""
    echo "⚠️  Setup completed but connection tests failed"
    echo "   Please check your configuration in .env1"
    echo ""
    exit 1
fi
