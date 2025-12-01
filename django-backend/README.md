# Security Monitoring Backend - Django REST API

This is the Django backend for the Security Operations Center Dashboard.

## Setup Instructions

### 1. Install Dependencies

```bash
cd django-backend
pip install -r requirements.txt
```

### 2. Configure Database

Make sure PostgreSQL is running and create the database:

```bash
psql -U postgres
CREATE DATABASE security_monitor;
\q
```

Update database credentials in `backend/settings.py` if needed.

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Create Sample Data (Important for testing)

You can create sample data through Django shell:

```bash
python manage.py shell
```

Then in the shell:

```python
from security_api.models import SecurityTool, Vulnerability, SecurityAlert

# Create tools
tools_data = [
    {'name': 'nmap', 'status': 'active', 'description': 'Network mapper and scanner'},
    {'name': 'zap', 'status': 'active', 'description': 'OWASP ZAP web scanner'},
    {'name': 'openvas', 'status': 'inactive', 'description': 'Vulnerability scanner'},
    {'name': 'trivy', 'status': 'active', 'description': 'Container security scanner'},
    {'name': 'wazuh', 'status': 'active', 'description': 'SIEM and security monitoring'},
    {'name': 'wireshark', 'status': 'active', 'description': 'Network protocol analyzer'},
]

for tool_data in tools_data:
    SecurityTool.objects.get_or_create(**tool_data)

# Create vulnerabilities
nmap = SecurityTool.objects.get(name='nmap')
zap = SecurityTool.objects.get(name='zap')

vulnerabilities = [
    {
        'title': 'SQL Injection in login form',
        'severity': 'critical',
        'status': 'open',
        'affected_asset': 'webapp.example.com',
        'description': 'SQL injection vulnerability in authentication endpoint',
        'cve_id': 'CVE-2024-1234',
        'tool': zap
    },
    {
        'title': 'Open SSH port detected',
        'severity': 'medium',
        'status': 'open',
        'affected_asset': '192.168.1.100',
        'description': 'SSH port 22 is publicly accessible',
        'tool': nmap
    },
]

for vuln in vulnerabilities:
    Vulnerability.objects.get_or_create(**vuln)

# Create alerts
alerts = [
    {
        'alert_type': 'intrusion',
        'severity': 'critical',
        'message': 'Brute force attack detected on SSH',
        'source': '192.168.1.50',
        'acknowledged': False,
        'tool': nmap
    },
    {
        'alert_type': 'vulnerability',
        'severity': 'high',
        'message': 'Critical vulnerability discovered',
        'source': 'webapp.example.com',
        'acknowledged': False,
        'tool': zap
    },
]

for alert in alerts:
    SecurityAlert.objects.get_or_create(**alert)

print("Sample data created successfully!")
```

### 6. Start Backend Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### 7. Start Frontend

In a separate terminal, from the root directory:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173/` and will automatically connect to the Django backend.

## API Endpoints

### Dashboard
- `GET /api/dashboard/` - Get comprehensive dashboard statistics

### Vulnerabilities
- `GET /api/vulnerabilities/` - List all vulnerabilities
- `GET /api/vulnerabilities/{id}/` - Get specific vulnerability
- `GET /api/vulnerabilities/by_severity/` - Get counts by severity
- `GET /api/vulnerabilities/recent/` - Get recent vulnerabilities

### Alerts
- `GET /api/alerts/` - List all alerts
- `GET /api/alerts/unacknowledged/` - Get unacknowledged alerts
- `POST /api/alerts/{id}/acknowledge/` - Acknowledge an alert

### Security Tools
- `GET /api/tools/` - List all tools
- `POST /api/tools/{id}/start_scan/` - Start a scan
- `POST /api/tools/{id}/stop_scan/` - Stop a scan

### Hosts
- `GET /api/hosts/` - List all network hosts

### Scan Results
- `GET /api/scans/` - List all scan results

### Metrics
- `GET /api/metrics/` - List all security metrics

## Testing the Integration

1. Make sure PostgreSQL is running
2. Start the Django backend: `python manage.py runserver`
3. Create sample data using the shell commands above
4. Start the React frontend: `npm run dev`
5. Open `http://localhost:5173/` in your browser
6. You should see real data from the Django backend!

## Optional: Celery for Background Tasks

To enable background task processing:

### 1. Install Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
```

### 2. Start Celery Worker

```bash
celery -A backend worker --loglevel=info
```

### 3. Start Celery Beat (for scheduled tasks)

```bash
celery -A backend beat --loglevel=info
```

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/` using your superuser credentials.

You can create, edit, and delete data directly from the admin interface.

## CORS Configuration

CORS is configured to allow requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:8080`

Update `CORS_ALLOWED_ORIGINS` in `backend/settings.py` if you need different origins.

## Troubleshooting

### Frontend shows "Loading..." forever
- Check that Django backend is running on port 8000
- Check browser console for CORS errors
- Verify you have sample data in the database

### Database Connection Error
- Ensure PostgreSQL is running
- Check database credentials in `settings.py`
- Make sure database `security_monitor` exists

### CORS errors
- Verify CORS settings in `backend/settings.py`
- Make sure `corsheaders` is in INSTALLED_APPS
- Check that frontend is running on `localhost:5173`

## Environment Variables

For production, create a `.env` file based on `.env.example` and update:
- `SECRET_KEY`
- `DEBUG=False`
- Database credentials
- `ALLOWED_HOSTS`
