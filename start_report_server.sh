#!/bin/bash
# Start Report Server for Deep Instinct HTML Reports

echo "=================================="
echo "  🌐 Starting Report Server..."
echo "=================================="
echo ""
echo "Server will serve HTML reports on port 8080"
echo ""
echo "📝 Update .env1 with your server IP:"
echo "   REPORT_SERVER_URL=http://YOUR_SERVER_IP:8080"
echo ""
echo "Press Ctrl+C to stop server"
echo ""
echo "=================================="

cd /home/api/DeepInstint
python3 serve_reports.py
