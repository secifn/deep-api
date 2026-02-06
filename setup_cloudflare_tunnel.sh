#!/bin/bash
# Setup Cloudflare Tunnel for Report Server

echo "=================================="
echo "  ☁️  Cloudflare Tunnel Setup"
echo "=================================="
echo ""
echo "Cloudflare Tunnel จะทำให้ server เข้าถึงได้จากภายนอกโดยไม่ต้องเปิด port"
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "📥 Installing cloudflared..."
    
    # Download and install
    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared-linux-amd64.deb
    rm cloudflared-linux-amd64.deb
    
    echo "✅ Cloudflared installed"
    echo ""
fi

echo "=================================="
echo "  🚀 Starting Cloudflare Tunnel"
echo "=================================="
echo ""
echo "Running: cloudflared tunnel --url http://localhost:8080"
echo ""
echo "⚠️  Copy the public URL that appears below"
echo "    and update .env1 with: REPORT_SERVER_URL=<that-url>"
echo ""
echo "=================================="
echo ""

cloudflared tunnel --url http://localhost:8080
