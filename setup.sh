#!/bin/bash

echo "======================================"
echo "Security Orchestration Platform Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose found${NC}"
echo ""

# Build and start containers
echo "Building and starting containers..."
docker-compose up -d --build

echo ""
echo "Waiting for services to start..."
sleep 10

# Run Django migrations
echo ""
echo "Running database migrations..."
docker-compose exec -T django python manage.py makemigrations
docker-compose exec -T django python manage.py migrate

# Create superuser prompt
echo ""
echo "Would you like to create a Django admin superuser? (y/n)"
read -r create_superuser

if [ "$create_superuser" = "y" ]; then
    docker-compose exec django python manage.py createsuperuser
fi

# Initialize security tools
echo ""
echo "Initializing security tools..."
docker-compose exec -T django python scripts/tool_integrations.py init

# Generate sample data
echo ""
echo "Would you like to generate sample data for testing? (y/n)"
read -r generate_sample

if [ "$generate_sample" = "y" ]; then
    docker-compose exec -T django python scripts/tool_integrations.py sample
fi

# Setup Elasticsearch indices
echo ""
echo "Setting up Elasticsearch indices..."
sleep 5  # Wait for Elasticsearch to be ready
docker-compose exec -T django python scripts/elasticsearch_integration.py create

echo ""
echo -e "${GREEN}======================================"
echo "Setup Complete!"
echo "======================================${NC}"
echo ""
echo "Services running at:"
echo -e "${YELLOW}Frontend:${NC}         http://localhost:5173"
echo -e "${YELLOW}Django API:${NC}       http://localhost:8000"
echo -e "${YELLOW}Django Admin:${NC}     http://localhost:8000/admin"
echo -e "${YELLOW}Kibana:${NC}           http://localhost:5601"
echo -e "${YELLOW}Elasticsearch:${NC}    http://localhost:9200"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop all services:"
echo "  docker-compose down"
echo ""
echo "To start services again:"
echo "  docker-compose up -d"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Start the React frontend: npm run dev"
echo "2. Access the dashboard at http://localhost:5173"
echo "3. Check Kibana for log visualization at http://localhost:5601"
echo "4. Run security scans using the integration scripts"
echo ""
