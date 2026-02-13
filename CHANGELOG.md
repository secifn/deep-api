# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Docker Compose support for easy deployment
- Makefile for simplified operations
- Production-ready Docker configuration
- Nginx reverse proxy support
- Automated health checks
- GitHub Actions CI/CD workflow
- Comprehensive documentation
  - README_DOCKER.md
  - QUICKSTART_DOCKER.md
  - DEPLOYMENT.md
  - DOCKER_CHEATSHEET.md

### Changed
- Environment variable loading now supports both .env and .env1
- Python scripts adapted for Docker environment
- Improved logging and error handling

### Fixed
- Hardcoded paths now use environment variables
- CORS headers properly configured

## [1.0.0] - 2026-02-13

### Added
- Initial prototype release
- Deep Instinct API integration
- Mattermost webhook notifications
- HTML report generation
- IT Parcel/Snip IT integration
- Daily report scheduler
- Real-time event monitoring
- Bangkok timezone support (GMT+7)
- Pagination support for large datasets
- Severity-based event classification
- Responsive HTML report design

### Features
- Malicious and suspicious event detection
- Device ownership lookup via Snip IT
- Department and division tracking
- File hash and path reporting
- Threat severity analysis
- Action tracking (DETECTED/PREVENTED)

### Documentation
- README.md - Main documentation
- README_INTEGRATION.md - Integration guide
- README_REPORTS.md - Report system guide
- ROADMAP.md - Development roadmap
- QUICKSTART.md - Quick start guide

### Scripts
- `send_today_to_mattermost.py` - Daily report generator
- `deepinstinct_to_mattermost.py` - Real-time monitor
- `serve_reports.py` - HTTP report server
- `test_connection.py` - Connection tester
- `fetch_snipit_devices.py` - Device lookup utility

### Configuration
- `.env.example` - Environment template
- Shell scripts for service management
- Systemd service files (optional)

## [0.1.0] - Initial Development

### Added
- Basic API connection
- Simple event fetching
- Console output logging
- Manual report generation

---

## Version History

- **1.0.0** - Production prototype with full features
- **0.1.0** - Initial development version

## Migration Guide

### From 0.1.0 to 1.0.0

1. Update Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Update environment file:
   ```bash
   cp .env.example .env1
   # Copy your existing credentials
   ```

3. Test new features:
   ```bash
   python3 test_connection.py
   python3 send_today_to_mattermost.py
   ```

### From 1.0.0 to Docker (Current)

1. Install Docker and Docker Compose

2. Create new .env file:
   ```bash
   cp .env.docker .env
   # Copy your credentials from .env1
   ```

3. Deploy with Docker:
   ```bash
   make install
   make up
   ```

4. Verify deployment:
   ```bash
   make ps
   make logs
   ```

## Breaking Changes

### 1.0.0 → Docker

- Environment file location changed from `/home/api/DeepInstint/.env1` to `.env`
- Services now run in containers instead of bare metal
- Port configuration via environment variables
- Cron jobs managed by Docker instead of system cron

### Compatibility Notes

- Python 3.7+ required
- Docker Engine 20.10+ for Docker deployment
- Docker Compose 2.0+ for Docker deployment

## Security Updates

- All credentials now via environment variables
- Container security hardening
- No privileged containers
- Network isolation between services

## Performance Improvements

- Docker multi-stage builds
- Optimized image sizes
- Health checks for automatic recovery
- Resource limits for stability

---

**Note**: This project follows [Semantic Versioning](https://semver.org/).

For detailed information about each release, see the [Releases](https://github.com/your-repo/releases) page.
