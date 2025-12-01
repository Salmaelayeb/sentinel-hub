# Security Orchestration Platform - Complete Setup Guide

## 🚀 Quick Start (Docker - Recommended)

### Prerequisites
- Docker & Docker Compose installed
- Git
- Node.js 18+ (for frontend development)

### Automated Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd security-platform

# Run automated setup
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Build and start all Docker containers
2. Initialize the database
3. Create security tool configurations
4. Setup Elasticsearch indices
5. Optionally generate sample data

### Start Frontend Development Server

```bash
# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Access the dashboard at **http://localhost:5173**

---

## 📋 Manual Setup (Without Docker)

### 1. Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip postgresql redis-server \
    elasticsearch kibana nmap
```

#### macOS
```bash
brew install python3 postgresql redis elasticsearch kibana nmap
brew services start postgresql
brew services start redis
brew services start elasticsearch
brew services start kibana
```

### 2. Setup PostgreSQL Database

```bash
# Create database
sudo -u postgres psql
CREATE DATABASE security_monitor;
CREATE USER security_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE security_monitor TO security_user;
\q
```

### 3. Setup Django Backend

```bash
cd django-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
nano .env

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Initialize security tools
python scripts/tool_integrations.py init

# Generate sample data (optional)
python scripts/tool_integrations.py sample

# Start Django server
python manage.py runserver
```

### 4. Setup Celery Workers

```bash
# Terminal 1 - Celery Worker
celery -A backend worker --loglevel=info

# Terminal 2 - Celery Beat (Scheduler)
celery -A backend beat --loglevel=info
```

### 5. Setup Elasticsearch

```bash
# Initialize indices
python scripts/elasticsearch_integration.py create

# Sync existing data
python scripts/elasticsearch_integration.py sync
```

### 6. Setup Frontend

```bash
cd ..  # Return to root directory
npm install
npm run dev
```

---

## 🔧 Configuration

### Environment Variables

#### Backend (.env in django-backend/)
```env
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_NAME=security_monitor
DATABASE_USER=security_user
DATABASE_PASSWORD=secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

ELASTICSEARCH_HOST=localhost:9200

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8080
```

#### Frontend (.env in root directory)
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## 🛠️ Installing Security Tools

### Nmap (Network Scanner)
```bash
# Ubuntu/Debian
sudo apt-get install nmap

# macOS
brew install nmap
```

### OWASP ZAP (Web Scanner)
```bash
# Download from https://www.zaproxy.org/download/
# Or use Docker
docker pull owasp/zap2docker-stable
```

### Trivy (Container Scanner)
```bash
# Ubuntu/Debian
wget https://github.com/aquasecurity/trivy/releases/download/v0.48.0/trivy_0.48.0_Linux-64bit.deb
sudo dpkg -i trivy_0.48.0_Linux-64bit.deb

# macOS
brew install aquasecurity/trivy/trivy
```

### OpenVAS (Vulnerability Scanner)
```bash
# Using Docker (Recommended)
docker run -d -p 9392:9392 --name openvas mikesplain/openvas
```

### Wireshark/TShark (Network Analyzer)
```bash
# Ubuntu/Debian
sudo apt-get install tshark wireshark

# macOS
brew install wireshark
```

### Wazuh (SIEM)
```bash
# Follow official guide: https://documentation.wazuh.com/current/installation-guide/
# Or use Docker
docker-compose -f wazuh-docker.yml up -d
```

---

## 🎯 Running Security Scans

### Nmap Network Scan
```bash
cd django-backend
python scripts/nmap_integration.py 192.168.1.0/24 --scan-type basic
```

### ZAP Web Scan
```bash
# Manual trigger through Django admin or API
curl -X POST http://localhost:8000/api/tools/2/start_scan/
```

### Trivy Container Scan
```bash
# Via Celery task
python manage.py shell
>>> from security_api.tasks import run_trivy_scan
>>> run_trivy_scan.delay('nginx:latest')
```

### Wireshark Traffic Capture
```bash
python scripts/wireshark_integration.py --interface eth0 --duration 300
```

---

## 📊 Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend Dashboard | http://localhost:5173 | - |
| Django API | http://localhost:8000/api | - |
| Django Admin | http://localhost:8000/admin | superuser credentials |
| Kibana | http://localhost:5601 | - |
| Elasticsearch | http://localhost:9200 | - |
| PostgreSQL | localhost:5432 | see .env |
| Redis | localhost:6379 | - |

---

## 🔍 Testing the Platform

### 1. Check Services Status
```bash
# Using Docker
docker-compose ps

# Manual
curl http://localhost:8000/api/dashboard/
curl http://localhost:9200/_cluster/health
```

### 2. View Logs
```bash
# Docker logs
docker-compose logs -f django
docker-compose logs -f celery_worker

# Manual
tail -f django-backend/logs/django.log
```

### 3. Run a Test Scan
```bash
# Initialize tools first
docker-compose exec django python scripts/tool_integrations.py init

# Generate sample data
docker-compose exec django python scripts/tool_integrations.py sample

# Refresh the frontend dashboard
```

---

## 🚨 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres
# or
sudo systemctl status postgresql

# Check connection
psql -h localhost -U security_user -d security_monitor
```

### Elasticsearch Not Starting
```bash
# Increase virtual memory
sudo sysctl -w vm.max_map_count=262144

# Check Elasticsearch logs
docker-compose logs elasticsearch
```

### Frontend Can't Connect to Backend
```bash
# Check CORS settings in backend/settings.py
# Verify API_BASE_URL in frontend .env
# Check Django is running on port 8000
```

### Celery Tasks Not Running
```bash
# Check Redis connection
redis-cli ping

# Check Celery worker logs
docker-compose logs celery_worker
```

---

## 📈 Next Steps

### 1. Configure Kibana Dashboards
- Access Kibana at http://localhost:5601
- Import index patterns for security-*
- Create visualization dashboards
- Setup alerting rules

### 2. Schedule Automated Scans
Edit `django-backend/backend/celery.py` to configure periodic tasks:
```python
app.conf.beat_schedule = {
    'nightly-network-scan': {
        'task': 'security_api.tasks.run_nmap_scan',
        'schedule': crontab(hour=2, minute=0),
        'args': ('192.168.1.0/24',)
    },
}
```

### 3. Setup Alerting
- Configure email notifications in Django settings
- Setup Slack/Discord webhooks for critical alerts
- Configure Kibana alerting for Elasticsearch data

### 4. Customize Tool Configurations
- Adjust scan parameters in tool integration scripts
- Configure vulnerability severity thresholds
- Setup custom detection rules

### 5. Production Deployment
- Change `DEBUG=False` in Django settings
- Use proper SECRET_KEY
- Setup HTTPS with nginx reverse proxy
- Configure firewall rules
- Setup backups for PostgreSQL and Elasticsearch
- Use Docker Swarm or Kubernetes for orchestration

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Elasticsearch Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Nmap Documentation](https://nmap.org/docs.html)
- [OWASP ZAP User Guide](https://www.zaproxy.org/docs/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Wazuh Documentation](https://documentation.wazuh.com/)

---

## 🤝 Support

For issues and questions:
1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check Django admin for tool status
4. Verify all services are running

---

## 📝 License

This project is for educational and security research purposes.
