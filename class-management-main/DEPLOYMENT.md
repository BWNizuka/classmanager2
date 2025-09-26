# Deployment Guide

This guide provides detailed instructions for deploying the Class Management System in various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Deployment](#development-deployment)
3. [Production Deployment](#production-deployment)
4. [Cloud Deployments](#cloud-deployments)
5. [Database Setup](#database-setup)
6. [Monitoring Setup](#monitoring-setup)
7. [SSL/HTTPS Configuration](#ssl-https-configuration)
8. [Backup and Recovery](#backup-and-recovery)
9. [Scaling](#scaling)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **Docker**: 20.10+ and Docker Compose 2.0+
- **Memory**: Minimum 2GB RAM, Recommended 4GB+
- **Storage**: Minimum 10GB free space
- **Network**: Ports 80, 443, 8000, 8501, 27017, 6379

### Required Tools

```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

## Development Deployment

### Quick Start

1. **Clone and Setup**
```bash
git clone https://github.com/yourusername/class-management.git
cd class-management
cp .env.example .env
```

2. **Configure Environment**
```bash
# Edit .env file
nano .env

# Key settings for development
APP_ENV=development
DATABASE_TYPE=sqlite
API_DEBUG=true
ENABLE_RELOAD=true
```

3. **Deploy with Docker Compose**
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

4. **Access Applications**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- MongoDB Express (if enabled): http://localhost:8081

### Development Services

The development environment includes:
- **Backend**: FastAPI with hot-reload
- **Frontend**: Streamlit with auto-restart
- **Database**: MongoDB with initialization scripts
- **Cache**: Redis for sessions
- **Proxy**: Nginx for routing

## Production Deployment

### Production Environment Setup

1. **Prepare Production Configuration**
```bash
# Copy and edit production environment
cp .env.example .env.prod

# Key production settings
APP_ENV=production
DATABASE_TYPE=mongodb
API_DEBUG=false
ENABLE_RELOAD=false
LOG_LEVEL=WARNING
```

2. **Security Configuration**
```bash
# Generate secure keys
openssl rand -hex 32  # For SECRET_KEY
openssl rand -hex 32  # For JWT_SECRET_KEY

# Set strong database passwords
MONGODB_USERNAME=admin
MONGODB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
```

3. **Deploy Production Stack**
```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

### Production Optimizations

**Resource Limits**
```yaml
# In docker-compose.prod.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 1G
    reservations:
      cpus: '1.0'
      memory: 512M
```

**Health Checks**
- All services have health check endpoints
- Automatic restart on failure
- Rolling updates support

**Security Features**
- Non-root containers
- Read-only filesystems where possible
- Network isolation
- Secret management

## Cloud Deployments

### AWS Deployment

#### AWS ECS/Fargate

1. **Setup AWS CLI**
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure credentials
aws configure
```

2. **Create ECR Repository**
```bash
# Create repository
aws ecr create-repository --repository-name class-management --region us-west-2

# Get login token
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com
```

3. **Build and Push Images**
```bash
# Build production image
docker build --target production -t class-management:latest .

# Tag for ECR
docker tag class-management:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/class-management:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/class-management:latest
```

4. **Deploy ECS Service**
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name class-management

# Create task definition (see aws/task-definition.json)
aws ecs register-task-definition --cli-input-json file://aws/task-definition.json

# Create service
aws ecs create-service \
  --cluster class-management \
  --service-name class-management-service \
  --task-definition class-management:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

#### AWS Lambda (Serverless)

For lighter workloads, deploy as serverless functions:

```bash
# Install Serverless Framework
npm install -g serverless
serverless create --template aws-python3 --path class-management-serverless

# Deploy
serverless deploy
```

### Google Cloud Platform

#### Google Cloud Run

1. **Setup gcloud CLI**
```bash
# Install gcloud
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

2. **Configure Docker for GCP**
```bash
gcloud auth configure-docker
```

3. **Build and Deploy**
```bash
# Build image
docker build --target production -t gcr.io/PROJECT-ID/class-management:latest .

# Push to Container Registry
docker push gcr.io/PROJECT-ID/class-management:latest

# Deploy to Cloud Run
gcloud run deploy class-management \
  --image gcr.io/PROJECT-ID/class-management:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --concurrency 100 \
  --timeout 300 \
  --set-env-vars APP_ENV=production,DATABASE_TYPE=mongodb
```

#### Google Kubernetes Engine (GKE)

```bash
# Create GKE cluster
gcloud container clusters create class-management \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-medium \
  --disk-size 50GB

# Get credentials
gcloud container clusters get-credentials class-management --zone us-central1-a

# Deploy with Kubernetes manifests
kubectl apply -f k8s/
```

### Microsoft Azure

#### Azure Container Instances

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create resource group
az group create --name ClassManagement --location eastus

# Deploy container
az container create \
  --resource-group ClassManagement \
  --name class-management \
  --image <registry>/class-management:latest \
  --dns-name-label class-management-app \
  --ports 8000 \
  --environment-variables \
    APP_ENV=production \
    DATABASE_TYPE=mongodb \
  --secure-environment-variables \
    SECRET_KEY=<secret> \
    JWT_SECRET_KEY=<jwt-secret>
```

## Database Setup

### MongoDB Production Setup

#### MongoDB Atlas (Recommended)

1. **Create MongoDB Atlas Cluster**
   - Go to https://cloud.mongodb.com
   - Create new cluster
   - Configure network access
   - Create database user

2. **Configure Connection**
```bash
# In .env.prod
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE_NAME=class_management
```

#### Self-hosted MongoDB

```bash
# MongoDB with authentication
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secure_password \
  -v mongodb_data:/data/db \
  mongo:7.0

# Create application database and user
mongosh "mongodb://admin:secure_password@localhost:27017/admin"
```

```javascript
// In MongoDB shell
use class_management
db.createUser({
  user: "app_user",
  pwd: "app_password",
  roles: [{ role: "readWrite", db: "class_management" }]
})
```

### SQLite Setup (Development)

SQLite is automatically configured for development:

```bash
# Database file location
./class_management.db

# Automatic table creation on first run
# No additional setup required
```

## Monitoring Setup

### Prometheus and Grafana

1. **Enable Monitoring Stack**
```bash
# Start with monitoring profile
docker-compose -f docker-compose.prod.yml --profile monitoring up -d
```

2. **Configure Prometheus**
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['backend:8000']
  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb:27017']
```

3. **Access Monitoring**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Custom Metrics

Add application metrics to FastAPI:

```python
from prometheus_client import Counter, Histogram
import time

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(process_time)
    
    return response
```

## SSL/HTTPS Configuration

### Let's Encrypt with Certbot

1. **Install Certbot**
```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

2. **Obtain SSL Certificate**
```bash
sudo certbot certonly --webroot -w /var/www/html -d yourdomain.com
```

3. **Configure Nginx**
```nginx
# nginx/prod.conf
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. **Auto-renewal**
```bash
# Add to crontab
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Custom SSL Certificates

For custom certificates:

```bash
# Create certificates directory
mkdir -p nginx/ssl

# Copy certificates
cp yourdomain.crt nginx/ssl/
cp yourdomain.key nginx/ssl/

# Update nginx configuration
# ssl_certificate /etc/ssl/certs/yourdomain.crt;
# ssl_certificate_key /etc/ssl/certs/yourdomain.key;
```

## Backup and Recovery

### Database Backup

#### MongoDB Backup

```bash
# Create backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Create backup
mongodump --uri="$MONGODB_URL" --out="$BACKUP_DIR/backup_$DATE"

# Compress backup
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" -C "$BACKUP_DIR" "backup_$DATE"
rm -rf "$BACKUP_DIR/backup_$DATE"

# Keep only last 7 backups
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.tar.gz"
EOF

chmod +x scripts/backup.sh
```

#### Automated Backups

```yaml
# In docker-compose.prod.yml
backup:
  image: mongo:7.0
  environment:
    MONGODB_URL: ${MONGODB_URL}
  volumes:
    - ./backups:/backups
    - ./scripts/backup.sh:/backup.sh:ro
  command: |
    sh -c "
      echo '0 2 * * * /backup.sh' | crontab -
      crond -f
    "
```

### Restore Procedures

```bash
# Restore from backup
mongorestore --uri="$MONGODB_URL" --drop backup_20240823_020000/

# Verify restore
mongosh "$MONGODB_URL" --eval "db.students.countDocuments()"
```

### Application Data Backup

```bash
# Backup application files
docker run --rm \
  -v class-management_app_data:/data \
  -v $(pwd)/backups:/backup \
  alpine:latest \
  tar czf /backup/app_data_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

## Scaling

### Horizontal Scaling

#### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml class-management

# Scale services
docker service scale class-management_backend=3
docker service scale class-management_frontend=2
```

#### Kubernetes

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: class-management-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: class-management:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Vertical Scaling

```yaml
# Increase resources in docker-compose.prod.yml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 2G
    reservations:
      cpus: '2.0'
      memory: 1G
```

### Load Balancing

```nginx
# nginx/prod.conf
upstream backend {
    least_conn;
    server backend1:8000 weight=3;
    server backend2:8000 weight=2;
    server backend3:8000 weight=1;
}

upstream frontend {
    ip_hash;
    server frontend1:8501;
    server frontend2:8501;
}
```

### Database Scaling

#### MongoDB Replica Set

```yaml
# docker-compose.mongodb-cluster.yml
mongodb-primary:
  image: mongo:7.0
  command: mongod --replSet rs0 --bind_ip_all
  
mongodb-secondary1:
  image: mongo:7.0
  command: mongod --replSet rs0 --bind_ip_all
  
mongodb-secondary2:
  image: mongo:7.0
  command: mongod --replSet rs0 --bind_ip_all
```

#### MongoDB Sharding

```bash
# Config servers
docker run -d --name mongocfg1 mongo:7.0 mongod --configsvr --replSet configReplSet

# Shard servers
docker run -d --name mongos1 mongo:7.0 mongod --shardsvr --replSet shard1ReplSet

# Mongos router
docker run -d --name mongos mongo:7.0 mongos --configdb configReplSet/mongocfg1:27019
```

## Troubleshooting

### Common Issues

#### Container Won't Start

```bash
# Check container logs
docker-compose logs service-name

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart service-name
```

#### Database Connection Issues

```bash
# Test MongoDB connection
mongosh "mongodb://username:password@localhost:27017/database"

# Check MongoDB logs
docker-compose logs mongodb

# Verify network connectivity
docker-compose exec backend ping mongodb
```

#### Memory Issues

```bash
# Check memory usage
docker stats

# Increase memory limits
# Edit docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 2G
```

#### SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in certificate.crt -text -noout

# Test SSL connection
openssl s_client -connect yourdomain.com:443

# Renew Let's Encrypt certificate
sudo certbot renew --dry-run
```

### Performance Troubleshooting

#### Slow API Responses

```bash
# Enable FastAPI debug logging
LOG_LEVEL=DEBUG

# Monitor database queries
# Add to MongoDB: db.setProfilingLevel(2)

# Check resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
```

#### High Memory Usage

```bash
# Identify memory-intensive containers
docker stats --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Analyze memory leaks
# Add memory profiling to application
import psutil
process = psutil.Process()
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

#### Database Performance

```bash
# MongoDB query optimization
db.students.createIndex({ "email": 1 })
db.students.createIndex({ "student_id": 1 })

# Monitor slow queries
db.setProfilingLevel(1, { slowms: 100 })
db.system.profile.find().limit(5).sort({ ts: -1 }).pretty()
```

### Health Check Scripts

```bash
# scripts/health-check.sh
#!/bin/bash

# Check API health
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "API health check failed"
    exit 1
fi

# Check database connectivity
if ! mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "Database health check failed"
    exit 1
fi

echo "All services healthy"
```

### Log Analysis

```bash
# Centralized logging with ELK stack
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  elasticsearch:7.17.0

# Kibana dashboard
docker run -d \
  --name kibana \
  --link elasticsearch:elasticsearch \
  -p 5601:5601 \
  kibana:7.17.0

# Logstash for log processing
docker run -d \
  --name logstash \
  --link elasticsearch:elasticsearch \
  -v $(pwd)/logstash.conf:/usr/share/logstash/pipeline/logstash.conf \
  logstash:7.17.0
```

## Security Considerations

### Container Security

```dockerfile
# Use non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

# Read-only filesystem
docker run --read-only --tmpfs /tmp myimage
```

### Network Security

```yaml
# Isolate networks
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
```

### Secret Management

```bash
# Use Docker secrets (Swarm mode)
echo "my-secret" | docker secret create app-secret -

# Or use external secret management
# HashiCorp Vault, AWS Secrets Manager, etc.
```

This comprehensive deployment guide covers all aspects of deploying the Class Management System across different environments and platforms. Choose the deployment method that best fits your requirements and infrastructure constraints.