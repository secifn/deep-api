#!/bin/bash
# Setup Firewall for Report Server

echo "=================================="
echo "  🔥 Firewall Setup for Port 8080"
echo "=================================="
echo ""

# Check if firewall is active
if command -v ufw &> /dev/null; then
    echo "📌 Using UFW (Ubuntu Firewall)"
    echo ""
    
    # Check status
    UFW_STATUS=$(sudo ufw status | grep -c "Status: active")
    
    if [ "$UFW_STATUS" -eq 1 ]; then
        echo "✅ UFW is active"
        echo ""
        echo "Adding rule for port 8080..."
        sudo ufw allow 8080/tcp
        echo ""
        echo "Current rules:"
        sudo ufw status | grep 8080
    else
        echo "⚠️  UFW is not active"
        echo "Port 8080 should be accessible"
    fi
    
elif command -v firewall-cmd &> /dev/null; then
    echo "📌 Using firewalld (CentOS/RHEL)"
    echo ""
    echo "Adding rule for port 8080..."
    sudo firewall-cmd --permanent --add-port=8080/tcp
    sudo firewall-cmd --reload
    echo ""
    echo "✅ Port 8080 opened"
    
else
    echo "⚠️  No firewall detected (ufw or firewalld)"
    echo "Port 8080 should be accessible"
fi

echo ""
echo "=================================="
echo "  ✅ Firewall setup complete!"
echo "=================================="
echo ""
echo "🧪 Test access from another machine:"
echo "   http://192.168.200.70:8080/event_details_2026-02-03.html"
echo ""
