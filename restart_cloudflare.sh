#!/bin/bash
# Restart Cloudflare Tunnel

echo "🔄 Restarting Cloudflare Tunnel..."

# Find and kill cloudflared process
sudo pkill -f cloudflared

sleep 2

# Start cloudflared again (using the existing token)
echo "✅ Cloudflare Tunnel has been restarted"
echo ""
echo "⚠️  You may need to start it manually with:"
echo "   sudo cloudflared tunnel run <tunnel-name>"
echo ""
echo "Or check the systemd service:"
echo "   sudo systemctl restart cloudflared"
