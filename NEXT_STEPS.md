# 🚀 Next Steps - Local Testing Guide

## Overview
You now have a complete Security Orchestration Platform that integrates multiple open-source security tools. Follow these steps to test it locally.

---

## ⚡ Quick Start (Recommended)

### Option 1: Using Docker (Easiest)

```bash
# 1. Make the setup script executable
chmod +x setup.sh

# 2. Run automated setup
./setup.sh

# 3. Start frontend development server
npm install
npm run dev

# 4. Access the dashboard
# Open http://localhost:5173 in your browser
```

That's it! All backend services, databases, and tools are now running in Docker containers.

---

## 📋 Option 2: Manual Setup (Without Docker)

### Step 1: Install System Dependencies

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    redis-server \
    nmap \
    tshark wireshark
```

#### On macOS:
```bash
brew install python3 postgresql redis nmap wireshark
brew services start postgresql
brew services start redis
```

### Step 2: Setup PostgreSQL Database

```bash
# Start PostgreSQL (if not already running)
sudo systemctl start postgresql  # Linux
# or
brew services start postgresql   # macOS

# Create database
sudo -u postgres psql
```

In psql:
```sql
CREATE DATABASE security_monitor;
CREATE USER security_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE security_monitor TO security_user;
\q
```

### Step 3: Setup Django Backend

```bash
cd django-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
# Update DATABASE_PASSWORD to match what you set above
nano .env  # or use any text editor

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Create admin superuser
python manage.py createsuperuser
# Follow prompts to set username/password

# Initialize security tools in database
python scripts/tool_integrations.py init

# Generate sample data for testing
python scripts/tool_integrations.py sample
```

### Step 4: Start Backend Services

Open 3 terminal windows:

**Terminal 1 - Django Server:**
```bash
cd django-backend
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
cd django-backend
source venv/bin/activate
celery -A backend worker --loglevel=info
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
cd django-backend
source venv/bin/activate
celery -A backend beat --loglevel=info
```

### Step 5: Setup Frontend

Open a new terminal:
```bash
# Install Node dependencies
npm install

# Start development server
npm run dev
```

### Step 6: Access the Dashboard

Open your browser and navigate to:
- **Frontend Dashboard:** http://localhost:5173
- **Django Admin:** http://localhost:8000/admin
- **API Docs:** http://localhost:8000/api

---

## 🧪 Testing Security Tools

### 1. Test Nmap Network Scanner

```bash
cd django-backend
source venv/bin/activate

# Scan localhost
python scripts/nmap_integration.py 127.0.0.1 --scan-type basic

# Scan local network (adjust your network range)
python scripts/nmap_integration.py 192.168.1.0/24 --scan-type basic
```

**Expected Result:** 
- New vulnerabilities appear in the dashboard
- Network hosts are discovered
- Scan completion alert is created

### 2. Test Web Application Scanner (ZAP)

**Note:** ZAP needs to be running first.

```bash
# Start ZAP in daemon mode (in a separate terminal)
zap.sh -daemon -port 8080 -config api.disablekey=true

# Run scan
cd django-backend
python scripts/zap_integration.py http://testphp.vulnweb.com/ --scan-type quick
```

**Expected Result:**
- Web vulnerabilities appear in dashboard
- SQL injection, XSS, and other web vulns detected

### 3. Test Container Scanner (Trivy)

```bash
# Install Trivy first
# Ubuntu/Debian:
wget https://github.com/aquasecurity/trivy/releases/download/v0.48.0/trivy_0.48.0_Linux-64bit.deb
sudo dpkg -i trivy_0.48.0_Linux-64bit.deb

# macOS:
brew install aquasecurity/trivy/trivy

# Scan a Docker image
cd django-backend
python manage.py shell
```

In the Django shell:
```python
from security_api.tasks import run_trivy_scan
result = run_trivy_scan.delay('nginx:latest')
print(result.get())
```

**Expected Result:**
- Container vulnerabilities imported to database
- Dashboard shows new CVEs found in the image

### 4. Test Network Traffic Analysis (Wireshark)

```bash
cd django-backend

# Capture traffic for 60 seconds
# You may need sudo for packet capture
sudo python scripts/wireshark_integration.py --interface eth0 --duration 60

# Or on macOS:
sudo python scripts/wireshark_integration.py --interface en0 --duration 60
```

**Expected Result:**
- Network traffic captured
- Anomalies detected (if any suspicious traffic)
- Alerts created for port scans or abnormal patterns

---

## 🔍 Verify Everything is Working

### 1. Check Dashboard Metrics

Visit http://localhost:5173 and verify:
- ✅ Critical vulnerabilities count shows data
- ✅ Active tools shows configured tools
- ✅ Systems monitored shows discovered hosts
- ✅ Alerts feed shows recent alerts
- ✅ Vulnerability table shows findings
- ✅ Tool status shows active/scanning states

### 2. Check Django Admin

Visit http://localhost:8000/admin and login with your superuser credentials.

Verify these sections have data:
- ✅ Security Tools
- ✅ Vulnerabilities
- ✅ Security Alerts
- ✅ Scan Results
- ✅ Network Hosts

### 3. Test API Endpoints

```bash
# Get dashboard stats
curl http://localhost:8000/api/dashboard/

# Get vulnerabilities
curl http://localhost:8000/api/vulnerabilities/

# Get alerts
curl http://localhost:8000/api/alerts/

# Get tools
curl http://localhost:8000/api/tools/
```

### 4. Test Real-time Updates

1. Start a scan from Django admin or via script
2. Watch the dashboard auto-refresh every 30 seconds
3. See tool status change to "scanning"
4. See new vulnerabilities appear when scan completes

---

## 🎯 Advanced Testing Scenarios

### Scenario 1: Full Network Assessment

```bash
# 1. Discover network hosts
python scripts/nmap_integration.py 192.168.1.0/24 --scan-type basic

# 2. Deep scan specific hosts
python scripts/nmap_integration.py 192.168.1.100 --scan-type vuln

# 3. Monitor network traffic
sudo python scripts/wireshark_integration.py --interface eth0 --duration 300

# 4. Check dashboard for complete assessment
```

### Scenario 2: Web Application Testing

```bash
# 1. Start ZAP
zap.sh -daemon -port 8080 -config api.disablekey=true

# 2. Quick scan
python scripts/zap_integration.py http://target.com --scan-type quick

# 3. Full scan
python scripts/zap_integration.py http://target.com --scan-type full

# 4. Review findings in dashboard
```

### Scenario 3: Container Security Audit

```bash
# Scan multiple container images
python manage.py shell
```

```python
from security_api.tasks import run_trivy_scan

# Scan multiple images
images = ['nginx:latest', 'alpine:latest', 'ubuntu:22.04', 'python:3.11']

for image in images:
    result = run_trivy_scan.delay(image)
    print(f"Scanning {image}...")

# Check dashboard after scans complete
```

---

## 📊 Optional: Setup Elasticsearch & Kibana

For advanced log analysis and visualization:

### Using Docker:
```bash
# Elasticsearch
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0

# Kibana
docker run -d \
  --name kibana \
  -p 5601:5601 \
  -e "ELASTICSEARCH_HOSTS=http://localhost:9200" \
  docker.elastic.co/kibana/kibana:8.11.0

# Wait for services to start (1-2 minutes)

# Initialize Elasticsearch indices
cd django-backend
python scripts/elasticsearch_integration.py create

# Sync existing data
python scripts/elasticsearch_integration.py sync
```

### Access Kibana:
- Open http://localhost:5601
- Create index patterns for `security-*`
- Build custom dashboards
- Setup alerting rules

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Check database connection
psql -h localhost -U security_user -d security_monitor

# Check for port conflicts
lsof -i :8000  # Django
lsof -i :6379  # Redis
```

### Frontend can't connect to backend
```bash
# Verify Django is running
curl http://localhost:8000/api/dashboard/

# Check CORS settings in django-backend/backend/settings.py
# Ensure 'http://localhost:5173' is in CORS_ALLOWED_ORIGINS
```

### Scans not running
```bash
# Verify Celery worker is running
# Check worker logs for errors

# Test Redis connection
redis-cli ping
# Should return: PONG

# Restart Celery worker
celery -A backend worker --loglevel=debug
```

### No data in dashboard
```bash
# Generate sample data
cd django-backend
python scripts/tool_integrations.py sample

# Check API returns data
curl http://localhost:8000/api/dashboard/

# Clear browser cache and refresh
```

---

## 📈 Production Deployment (Future)

When ready to deploy to production:

1. **Security Hardening**
   - Change `DEBUG=False` in Django settings
   - Use strong `SECRET_KEY`
   - Configure firewall rules
   - Enable HTTPS with SSL certificates
   - Setup proper authentication

2. **Database**
   - Use managed PostgreSQL service
   - Setup automated backups
   - Configure connection pooling

3. **Scalability**
   - Use Docker Swarm or Kubernetes
   - Setup load balancing
   - Configure auto-scaling for Celery workers
   - Use managed Redis service

4. **Monitoring**
   - Setup application monitoring (Sentry, DataDog)
   - Configure log aggregation
   - Setup uptime monitoring
   - Create runbooks for incidents

---

## 🎓 Learning Resources

- [Nmap Documentation](https://nmap.org/book/man.html)
- [OWASP ZAP User Guide](https://www.zaproxy.org/docs/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Wireshark User Guide](https://www.wireshark.org/docs/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Elasticsearch Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)

---

## ✅ Success Checklist

Before considering the project complete, verify:

- [ ] Django backend running without errors
- [ ] PostgreSQL database accessible
- [ ] Redis working for Celery
- [ ] Celery worker processing tasks
- [ ] Frontend displaying data from API
- [ ] Can create admin user and access Django admin
- [ ] Sample data appears in dashboard
- [ ] At least one security tool scan completed successfully
- [ ] Real-time updates working (refresh every 30s)
- [ ] Can acknowledge alerts
- [ ] Can start/stop tool scans from frontend

---

## 🤝 Need Help?

If you encounter issues:

1. Check logs:
   ```bash
   # Django logs
   tail -f django-backend/logs/django.log
   
   # Celery logs
   # Check terminal where celery worker is running
   ```

2. Review documentation:
   - `SETUP_GUIDE.md` - Complete setup instructions
   - `django-backend/README.md` - Backend specific info
   - `.env.example` - Environment variable reference

3. Verify all services are running:
   ```bash
   # Check processes
   ps aux | grep python
   ps aux | grep celery
   
   # Check ports
   lsof -i :5173  # Frontend
   lsof -i :8000  # Django
   lsof -i :6379  # Redis
   lsof -i :5432  # PostgreSQL
   ```

---

## 🎉 Congratulations!

You now have a fully functional Security Orchestration Platform! The system can:
- ✅ Discover network hosts and services
- ✅ Scan for vulnerabilities across multiple vectors
- ✅ Analyze network traffic for anomalies
- ✅ Aggregate findings in a unified dashboard
- ✅ Alert on critical security issues
- ✅ Automate scanning with Celery tasks
- ✅ Provide real-time monitoring capabilities

**Next:** Customize the tool configurations, add scheduled scans, and integrate additional security tools as needed!
