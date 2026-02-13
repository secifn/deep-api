#!/bin/bash
# Health check script for Docker containers

set -e

SERVICE_NAME="${SERVICE_NAME:-unknown}"
HEALTH_CHECK_TIMEOUT=5

case "$SERVICE_NAME" in
    "report-server")
        # Check if HTTP server is responding
        curl -f -s --max-time $HEALTH_CHECK_TIMEOUT http://localhost:8080/ > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "✅ Report server is healthy"
            exit 0
        else
            echo "❌ Report server is not responding"
            exit 1
        fi
        ;;
    
    "monitor")
        # Check if Python process is running
        if pgrep -f "deepinstinct_to_mattermost" > /dev/null 2>&1; then
            echo "✅ Monitor process is running"
            exit 0
        else
            echo "❌ Monitor process is not running"
            exit 1
        fi
        ;;
    
    "daily-report")
        # Check if cron is running
        if pgrep cron > /dev/null 2>&1; then
            echo "✅ Cron service is running"
            exit 0
        else
            echo "❌ Cron service is not running"
            exit 1
        fi
        ;;
    
    *)
        echo "⚠️  Unknown service: $SERVICE_NAME"
        exit 1
        ;;
esac
