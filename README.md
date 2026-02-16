# Deep Instinct to Mattermost Integration

🔒 ระบบเชื่อมต่อ Deep Instinct Security Events กับ Mattermost Notifications พร้อมระบบรายงานและ Device Management Integration

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](docker-compose.yml)
[![Python](https://img.shields.io/badge/Python-3.7+-green?logo=python)](requirements.txt)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Overview

ระบบนี้ดึงข้อมูล Security Events จาก Deep Instinct API และส่งการแจ้งเตือนไปยัง Mattermost พร้อมทั้งสร้างรายงาน HTML รายละเอียด รวมถึงการเชื่อมต่อกับ IT Parcel/Snip IT สำหรับข้อมูลผู้รับผิดชอบเครื่อง

### ✨ Features

- ✅ **Real-time Monitoring** - ตรวจสอบ events แบบ real-time
- ✅ **Daily Reports** - รายงานสรุปประจำวัน
- ✅ **HTML Reports** - รายงานละเอียดแบบ HTML พร้อม responsive design
- ✅ **Device Management Integration** - เชื่อมต่อ IT Parcel/Snip IT
- ✅ **Threat Severity Analysis** - วิเคราะห์ระดับความรุนแรง
- ✅ **Docker Support** - Deploy ง่ายด้วย Docker Compose
- ✅ **Timezone Support** - รองรับ Bangkok timezone (GMT+7)
- ✅ **Pagination Support** - ดึงข้อมูลจำนวนมากได้
- ✅ **SQLite Database** - เก็บ event history และป้องกันส่งซ้ำ ⭐ NEW
- ✅ **Query & Analytics** - ค้นหาและวิเคราะห์ events ⭐ NEW

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone repository
git clone <repo-url>
cd deep-api

# 2. Setup environment
make install
# Edit .env with your credentials

# 3. Start services
make up

# 4. View logs
make logs
```

**Full Docker documentation**: [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md)

### Option 2: Traditional Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env1
# Edit .env1 with your credentials

# 3. Run services
python3 serve_reports.py &
python3 deepinstinct_to_mattermost.py &

# 4. Setup cron for daily reports
crontab -e
# Add: 0 8 * * * cd /path/to/deep-api && python3 send_today_to_mattermost.py
```

## 📖 Documentation

- 🐳 **Docker Deployment**: [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md) | [README_DOCKER.md](README_DOCKER.md)
- 🏗️ **Production Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- 🔧 **Integration Guide**: [README_INTEGRATION.md](README_INTEGRATION.md)
- 📊 **Report System**: [README_REPORTS.md](README_REPORTS.md)
- 🗄️ **Database Guide**: [README_DATABASE.md](README_DATABASE.md) ⭐ NEW
- 🗺️ **Roadmap**: [ROADMAP.md](ROADMAP.md)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Compose Stack                  │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │Report Server │  │ Daily Report │  │   Monitor    │ │
│  │  (HTTP:8080) │  │   (Cron)     │  │ (Real-time)  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                  │          │
│         └─────────────────┴──────────────────┘          │
│                           │                             │
└───────────────────────────┼─────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
  Deep Instinct          Mattermost        IT Parcel
      API                Webhook           (Snip IT)
```

### Services

1. **Report Server** (Port 8080)
   - Serve HTML reports
   - CORS enabled
   - Health checks

2. **Daily Report** (Cron-based)
   - Generate daily summary
   - Send to Mattermost
   - Configurable schedule

3. **Monitor** (Continuous)
   - Real-time event polling
   - Instant notifications
   - Auto-recovery

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEEPINSTINCT_URL` | Deep Instinct API URL | ✅ |
| `TOKENS_KEY` | JWT Token | ✅ |
| `MATTERMOST_WEBHOOK_URL` | Mattermost Webhook | ✅ |
| `REPORT_SERVER_URL` | Report Server URL | ✅ |
| `IT_PARCEL_API_URL` | IT Parcel API (Optional) | ❌ |
| `IT_PARCEL_TOKEN` | IT Parcel Token (Optional) | ❌ |
| `POLLING_INTERVAL` | Monitor interval (seconds) | ❌ |
| `DAILY_REPORT_CRON` | Cron schedule | ❌ |

### Example Configuration

```env
# .env
DEEPINSTINCT_URL=https://ro.customers.deepinstinctweb.com/api/v1/
TOKENS_KEY=your_jwt_token
MATTERMOST_WEBHOOK_URL=https://mattermost.com/hooks/xxx
REPORT_SERVER_URL=http://report-server:8080
POLLING_INTERVAL=300
DAILY_REPORT_CRON=0 8 * * *
```

## 📊 Usage

### Docker Commands

```bash
# Start all services
make up

# View logs
make logs

# Run manual report
make report

# Run report for specific date
make report-date DATE=2026-02-13

# Stop services
make down

# View all commands
make help
```

### Python Scripts

```bash
# Daily report (today)
python3 send_today_to_mattermost.py

# Report for specific date
python3 send_today_to_mattermost.py 2026-02-13

# Start monitor
python3 deepinstinct_to_mattermost.py

# Start report server
python3 serve_reports.py
```

## 📈 Reports

Reports are generated in HTML format with:
- ✅ Event details and severity
- ✅ Device information
- ✅ Responsible person (from Snip IT)
- ✅ Department and division
- ✅ File hashes and paths
- ✅ Responsive design

**Access reports at**: `http://localhost:8080/event_detail/`

## 🔧 Development

### Setup Development Environment

```bash
# Clone and setup
git clone <repo-url>
cd deep-api

# Install dependencies
pip install -r requirements.txt

# Setup pre-commit hooks (optional)
pre-commit install

# Start development
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Project Structure

```
deep-api/
├── send_today_to_mattermost.py      # Daily report generator
├── deepinstinct_to_mattermost.py    # Real-time monitor
├── serve_reports.py                  # HTTP server
├── test_connection.py                # Connection tester
├── database.py                       # Database manager ⭐ NEW
├── query_events.py                   # Query events tool ⭐ NEW
├── db_maintenance.py                 # Database maintenance ⭐ NEW
├── docker-compose.yml                # Docker orchestration
├── Dockerfile                        # Container image
├── Makefile                          # Quick commands
├── requirements.txt                  # Python dependencies
├── data/
│   └── events.db                    # SQLite database ⭐ NEW
├── event_detail/                     # Generated reports
└── backups/                          # Database backups ⭐ NEW
```

## 🐛 Troubleshooting

### Common Issues

**Services not starting?**
```bash
make logs
```

**API connection failed?**
```bash
make test
```

**Port conflict?**
```bash
# Edit .env
REPORT_SERVER_PORT=8081
```

**For more help**: See [README_DOCKER.md](README_DOCKER.md#troubleshooting)

## 📊 Monitoring

### Health Checks

```bash
# Service status
docker-compose ps

# Health endpoint
curl http://localhost:8080/health

# Resource usage
docker stats
```

### Logs

```bash
# All logs
make logs

# Specific service
make logs-monitor
make logs-report
make logs-daily
```

## 🔒 Security

- ✅ Environment-based secrets
- ✅ Read-only containers where possible
- ✅ No privileged containers
- ✅ Network isolation
- ✅ Health checks enabled
- ✅ Auto-restart on failure

## 🎯 Roadmap

- [x] Phase 1: Prototype (Current)
- [ ] Phase 2: Production Ready
  - [ ] Database integration
  - [ ] Enhanced logging
  - [ ] Duplicate detection
  - [ ] Retry logic
- [ ] Phase 3: Advanced Features
  - [ ] Web dashboard
  - [ ] Alert customization
  - [ ] Historical analytics

Full roadmap: [ROADMAP.md](ROADMAP.md)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

[MIT License](LICENSE)

## 👥 Authors

- Your Team/Name Here

## 📞 Support

- 📖 Documentation: See `/docs` folder
- 🐛 Issues: Open an issue on GitHub
- 💬 Questions: Contact the team

---

**Built with ❤️ for Security Operations**

🚀 **Get Started**: [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md)
