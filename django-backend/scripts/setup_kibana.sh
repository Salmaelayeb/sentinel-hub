#!/bin/bash

echo "🔍 Testing Security Platform..."
echo ""

echo "1️⃣ Checking containers..."
docker-compose ps | grep -q "Up" && echo "✅ Containers running" || echo "❌ Containers not running"

echo "2️⃣ Checking PostgreSQL..."
docker-compose exec -T postgres psql -U postgres -d security_monitor -c "SELECT 1" > /dev/null 2>&1 && echo "✅ PostgreSQL working" || echo "❌ PostgreSQL failed"

echo "3️⃣ Checking Redis..."
docker-compose exec -T redis redis-cli ping | grep -q "PONG" && echo "✅ Redis working" || echo "❌ Redis failed"

echo "4️⃣ Checking Elasticsearch..."
curl -s http://localhost:9200/_cluster/health | grep -q "status" && echo "✅ Elasticsearch working" || echo "❌ Elasticsearch failed"

echo "5️⃣ Checking Django API..."
curl -s http://localhost:8000/api/ | grep -q "tools" && echo "✅ Django API working" || echo "❌ Django API failed"

echo "6️⃣ Checking Kibana..."
curl -s http://localhost:5601/api/status | grep -q "available" && echo "✅ Kibana working" || echo "❌ Kibana not ready"

echo ""
echo "✅ Health check complete!"