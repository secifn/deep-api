#!/bin/bash

# Docker Management Script for Deep API Production
# ใช้สำหรับจัดการ Docker Compose Production

set -e

COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_NAME="deep-api"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           Deep API - Production Management                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if docker-compose is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed!"
        exit 1
    fi
}

# Start services
start_services() {
    print_info "Starting Docker services..."
    docker-compose -f $COMPOSE_FILE up -d
    print_success "Services started!"
    echo ""
    status_services
}

# Stop services
stop_services() {
    print_info "Stopping Docker services..."
    docker-compose -f $COMPOSE_FILE down
    print_success "Services stopped!"
}

# Restart services
restart_services() {
    print_info "Restarting Docker services..."
    docker-compose -f $COMPOSE_FILE restart
    print_success "Services restarted!"
    echo ""
    status_services
}

# Status of services
status_services() {
    print_info "Docker services status:"
    echo ""
    docker-compose -f $COMPOSE_FILE ps
    echo ""
}

# View logs
view_logs() {
    local service=$1
    if [ -z "$service" ]; then
        print_info "Showing logs for all services (Ctrl+C to exit)..."
        docker-compose -f $COMPOSE_FILE logs -f --tail=100
    else
        print_info "Showing logs for service: $service (Ctrl+C to exit)..."
        docker-compose -f $COMPOSE_FILE logs -f --tail=100 $service
    fi
}

# Rebuild services
rebuild_services() {
    print_info "Rebuilding Docker images..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    print_success "Images rebuilt!"
    print_info "Restarting services..."
    docker-compose -f $COMPOSE_FILE up -d
    print_success "Services restarted with new images!"
}

# Execute command in container
exec_command() {
    local service=$1
    shift
    local cmd="$@"
    
    if [ -z "$service" ]; then
        print_error "Service name required!"
        echo "Usage: $0 exec <service> <command>"
        exit 1
    fi
    
    docker-compose -f $COMPOSE_FILE exec $service $cmd
}

# Run test in container
run_test() {
    local test_type=$1
    local date_arg=${2:-"yesterday"}
    
    case $test_type in
        format)
            print_info "Running format test (sample data)..."
            docker-compose -f $COMPOSE_FILE exec report-server python3 test_report_format.py
            ;;
        preview)
            print_info "Running preview test (real data, date: $date_arg)..."
            docker-compose -f $COMPOSE_FILE exec report-server python3 test_report_preview.py "$date_arg"
            ;;
        complete|full)
            print_info "Running complete test (real data + HTML, date: $date_arg)..."
            docker-compose -f $COMPOSE_FILE exec report-server python3 test_complete_report.py "$date_arg"
            ;;
        *)
            print_error "Unknown test type: $test_type"
            echo "Available tests: format, preview, complete"
            exit 1
            ;;
    esac
}

# Send report (production)
send_report() {
    local date_arg=${1:-"yesterday"}
    print_warning "Sending REAL report to Mattermost (date: $date_arg)..."
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        docker-compose -f $COMPOSE_FILE exec report-server python3 send_today_to_mattermost.py "$date_arg"
        print_success "Report sent!"
    else
        print_info "Cancelled."
    fi
}

# Query database
query_db() {
    local cmd="$@"
    if [ -z "$cmd" ]; then
        docker-compose -f $COMPOSE_FILE exec report-server python3 query_events.py --help
    else
        docker-compose -f $COMPOSE_FILE exec report-server python3 query_events.py $cmd
    fi
}

# Database maintenance
db_maintenance() {
    local action=$1
    case $action in
        backup)
            docker-compose -f $COMPOSE_FILE exec report-server python3 db_maintenance.py backup
            ;;
        vacuum)
            docker-compose -f $COMPOSE_FILE exec report-server python3 db_maintenance.py vacuum
            ;;
        stats)
            docker-compose -f $COMPOSE_FILE exec report-server python3 db_maintenance.py analyze
            ;;
        cleanup)
            docker-compose -f $COMPOSE_FILE exec report-server python3 db_maintenance.py cleanup --days 90
            ;;
        *)
            print_error "Unknown maintenance action: $action"
            echo "Available actions: backup, vacuum, stats, cleanup"
            exit 1
            ;;
    esac
}

# Show help
show_help() {
    print_header
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  start             - Start all services"
    echo "  stop              - Stop all services"
    echo "  restart           - Restart all services"
    echo "  status            - Show services status"
    echo "  logs [service]    - View logs (all or specific service)"
    echo "  rebuild           - Rebuild and restart services"
    echo ""
    echo "Testing Commands:"
    echo "  test format                    - Test message format (sample data)"
    echo "  test preview [date]            - Test with real data (no HTML)"
    echo "  test complete [date]           - Full test (real data + HTML)"
    echo ""
    echo "Production Commands:"
    echo "  send [date]                    - Send real report to Mattermost"
    echo "  query [options]                - Query database"
    echo "  db <backup|vacuum|stats|cleanup> - Database maintenance"
    echo ""
    echo "Container Commands:"
    echo "  exec <service> <command>       - Execute command in container"
    echo "  shell <service>                - Open shell in container"
    echo ""
    echo "Date formats:"
    echo "  yesterday                      - เมื่อวาน"
    echo "  2026-02-15                     - ค.ศ."
    echo "  15-2-69                        - พ.ศ. (วัน-เดือน-ปี)"
    echo ""
    echo "Examples:"
    echo "  $0 start                       - Start all services"
    echo "  $0 test complete yesterday     - Test with yesterday's data"
    echo "  $0 test complete 15-2-69       - Test with specific date"
    echo "  $0 send yesterday              - Send report for yesterday"
    echo "  $0 logs report-server          - View report-server logs"
    echo "  $0 query --date 2026-02-15     - Query events for date"
    echo "  $0 db backup                   - Backup database"
    echo ""
}

# Main
main() {
    check_docker
    
    local command=${1:-"help"}
    
    case $command in
        start)
            print_header
            start_services
            ;;
        stop)
            print_header
            stop_services
            ;;
        restart)
            print_header
            restart_services
            ;;
        status)
            print_header
            status_services
            ;;
        logs)
            shift
            view_logs "$@"
            ;;
        rebuild)
            print_header
            rebuild_services
            ;;
        exec)
            shift
            exec_command "$@"
            ;;
        shell)
            shift
            exec_command "$1" /bin/bash
            ;;
        test)
            shift
            print_header
            run_test "$@"
            ;;
        send)
            shift
            print_header
            send_report "$@"
            ;;
        query)
            shift
            print_header
            query_db "$@"
            ;;
        db)
            shift
            print_header
            db_maintenance "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
