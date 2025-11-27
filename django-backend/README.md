# Security Monitoring Platform - Django Backend

This is the Django REST API backend for the integrated security monitoring platform. It orchestrates security tools like Nmap, OWASP ZAP, OpenVAS, Trivy, Wazuh, and TShark.

## Features

- **REST API** for security data management
- **Database models** for vulnerabilities, alerts, scan results, and metrics
- **Celery tasks** for automated tool execution
- **Admin interface** for data management
- **Integration scripts** for security tools

## Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis (for Celery)
- Security tools installed:
  - Nmap
  - OWASP ZAP
  - OpenVAS
  - Trivy
  - Wireshark/TShark
  - Wazuh (optional)

## Installation

### 1. Create Virtual Environment

```bash
cd django-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

Create PostgreSQL database:

```sql
CREATE DATABASE security_monitor;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE security_monitor TO postgres;
```

Update `backend/settings.py` if needed with your database credentials.

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Initialize Security Tools

```bash
python scripts/tool_integrations.py init
```

### 7. Generate Sample Data (Optional)

```bash
python scripts/tool_integrations.py sample
```

## Running the Server

### Development Server

```bash
python manage.py runserver
```

API will be available at: `http://localhost:8000/api/`

### Run Celery Worker (for background tasks)

In a separate terminal:

```bash
celery -A backend worker -l info
```

### Run Celery Beat (for scheduled tasks)

In another terminal:

```bash
celery -A backend beat -l info
```

## API Endpoints

### Dashboard
- `GET /api/dashboard/` - Get comprehensive dashboard statistics

### Security Tools
- `GET /api/tools/` - List all security tools
- `GET /api/tools/{id}/` - Get tool details
- `POST /api/tools/{id}/start_scan/` - Start a scan
- `POST /api/tools/{id}/stop_scan/` - Stop a scan

### Vulnerabilities
- `GET /api/vulnerabilities/` - List all vulnerabilities
- `GET /api/vulnerabilities/{id}/` - Get vulnerability details
- `GET /api/vulnerabilities/by_severity/` - Get counts by severity
- `GET /api/vulnerabilities/recent/` - Get recent vulnerabilities
- `POST /api/vulnerabilities/` - Create vulnerability
- `PUT /api/vulnerabilities/{id}/` - Update vulnerability
- `DELETE /api/vulnerabilities/{id}/` - Delete vulnerability

### Alerts
- `GET /api/alerts/` - List all alerts
- `GET /api/alerts/{id}/` - Get alert details
- `POST /api/alerts/{id}/acknowledge/` - Acknowledge alert
- `GET /api/alerts/unacknowledged/` - Get unacknowledged alerts

### Scan Results
- `GET /api/scans/` - List all scan results
- `GET /api/scans/{id}/` - Get scan details

### Network Hosts
- `GET /api/hosts/` - List discovered hosts
- `GET /api/hosts/{id}/` - Get host details

### Metrics
- `GET /api/metrics/` - List security metrics

## Filtering & Search

Most endpoints support filtering and search:

```bash
# Filter vulnerabilities by severity
GET /api/vulnerabilities/?severity=critical

# Search vulnerabilities
GET /api/vulnerabilities/?search=sql+injection

# Filter alerts by type
GET /api/alerts/?alert_type=intrusion

# Pagination
GET /api/vulnerabilities/?page=2
```

## Running Manual Scans

### Nmap Scan

```bash
python scripts/tool_integrations.py nmap --target 192.168.1.0/24
```

## Celery Tasks

The following background tasks are available:

- `run_nmap_scan(target, scan_type)` - Execute Nmap scan
- `run_zap_scan(target_url)` - Execute OWASP ZAP scan
- `run_trivy_scan(image_name)` - Execute Trivy container scan
- `aggregate_daily_metrics()` - Aggregate daily metrics

### Trigger tasks manually:

```python
from security_api.tasks import run_nmap_scan

# Trigger async task
run_nmap_scan.delay('192.168.1.100', 'basic')
```

## Admin Interface

Access the admin interface at: `http://localhost:8000/admin/`

Use the superuser credentials you created earlier.

## Integration with React Frontend

The React frontend should connect to these endpoints. Update the React app's API base URL to:

```typescript
const API_BASE_URL = 'http://localhost:8000/api';
```

Make sure CORS is properly configured in `backend/settings.py` (already set for `localhost:5173`).

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker (Create Dockerfile)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Environment Variables

For production, use environment variables:

```bash
export SECRET_KEY='your-secret-key'
export DEBUG=False
export DATABASE_URL='postgresql://user:pass@localhost/db'
export ELASTICSEARCH_HOST='elasticsearch:9200'
```

## Security Notes

- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use strong database passwords
- Enable HTTPS
- Configure proper firewall rules
- Review CORS settings for production domains

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check database credentials in settings.py

### Celery Not Working
- Ensure Redis is running
- Check Celery broker URL

### Tool Execution Fails
- Ensure security tools are installed and in PATH
- Check tool permissions

## License

This project is part of the Security Monitoring Platform.
