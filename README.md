# Integrated Security Orchestration Platform

A comprehensive security monitoring platform integrating Wazuh, ELK Stack, Nmap, OWASP ZAP, Wireshark, OpenVAS, and Trivy.

## 🚀 Quick Start

### Automated Setup (Docker - Recommended)

```bash
chmod +x setup.sh
./setup.sh
npm install && npm run dev
```

Access dashboard at **http://localhost:5173**

### Manual Setup

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed instructions.

## 📚 Documentation

- **[NEXT_STEPS.md](./NEXT_STEPS.md)** - Local testing guide
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Complete setup instructions
- **[django-backend/README.md](./django-backend/README.md)** - Backend API docs

## 🛠️ Integrated Tools

- **Nmap** - Network scanning
- **OWASP ZAP** - Web vulnerability scanning
- **OpenVAS** - Comprehensive vulnerability assessment
- **Trivy** - Container security scanning
- **Wireshark/TShark** - Network traffic analysis
- **Wazuh** - SIEM and intrusion detection
- **ELK Stack** - Log aggregation and visualization

## 📊 Services

| Service | Port | URL |
|---------|------|-----|
| Frontend | 5173 | http://localhost:5173 |
| Django API | 8000 | http://localhost:8000 |
| Kibana | 5601 | http://localhost:5601 |
| Elasticsearch | 9200 | http://localhost:9200 |

## 🧪 Quick Test

```bash
cd django-backend
python scripts/tool_integrations.py sample
python scripts/nmap_integration.py 127.0.0.1 --scan-type basic
```

**Built with React, Django, and Open-Source Security Tools**
