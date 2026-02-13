#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Deep Instinct to Mattermost - Docker Container        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check required environment variables
if [ -z "$DEEPINSTINCT_URL" ] || [ -z "$TOKENS_KEY" ] || [ -z "$MATTERMOST_WEBHOOK_URL" ]; then
    echo -e "${RED}❌ Error: Missing required environment variables${NC}"
    echo ""
    echo "Required variables:"
    echo "  - DEEPINSTINCT_URL"
    echo "  - TOKENS_KEY"
    echo "  - MATTERMOST_WEBHOOK_URL"
    echo ""
    echo "Please check your .env file."
    exit 1
fi

# Service selection
SERVICE_MODE="${1:-report-server}"

echo -e "${GREEN}✅ Environment variables loaded${NC}"
echo -e "${BLUE}📦 Service Mode: ${SERVICE_MODE}${NC}"
echo ""

case "$SERVICE_MODE" in
    "report-server")
        echo -e "${GREEN}🌐 Starting HTTP Report Server...${NC}"
        exec python3 /app/serve_reports_docker.py
        ;;
    
    "daily-report")
        echo -e "${GREEN}📅 Starting Daily Report Service (Cron)...${NC}"
        
        # Install cron if not available
        apt-get update > /dev/null 2>&1 && apt-get install -y cron > /dev/null 2>&1
        
        # Get cron schedule from environment or use default (8 AM daily)
        CRON_SCHEDULE="${DAILY_REPORT_CRON:-0 8 * * *}"
        
        # Create cron job
        echo "$CRON_SCHEDULE cd /app && python3 /app/send_today_to_mattermost.py >> /app/logs/daily-report.log 2>&1" > /etc/cron.d/daily-report
        chmod 0644 /etc/cron.d/daily-report
        crontab /etc/cron.d/daily-report
        
        echo -e "${GREEN}✅ Cron job scheduled: ${CRON_SCHEDULE}${NC}"
        echo -e "${BLUE}ℹ️  Logs: /app/logs/daily-report.log${NC}"
        
        # Start cron in foreground
        cron && tail -f /app/logs/daily-report.log
        ;;
    
    "monitor")
        echo -e "${GREEN}🔍 Starting Continuous Monitor...${NC}"
        exec python3 /app/deepinstinct_to_mattermost_docker.py
        ;;
    
    "once")
        echo -e "${GREEN}🚀 Running Daily Report Once...${NC}"
        exec python3 /app/send_today_to_mattermost.py "$@"
        ;;
    
    *)
        echo -e "${RED}❌ Unknown service mode: $SERVICE_MODE${NC}"
        echo ""
        echo "Available modes:"
        echo "  - report-server  : Start HTTP server for reports"
        echo "  - daily-report   : Start cron-based daily report"
        echo "  - monitor        : Start continuous monitoring"
        echo "  - once          : Run daily report once"
        exit 1
        ;;
esac
