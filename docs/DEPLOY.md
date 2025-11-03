# AutoLabMate Deployment Guide

This guide covers deploying AutoLabMate to production environments.

---

## Deployment Options

### Option 1: Docker Compose (Recommended for VPS)

**Best for:** Single-server deployments, VPS instances, small teams

**Requirements:**
- VPS with 4+ GB RAM
- Docker and Docker Compose installed
- Domain name (optional, for HTTPS)

**Steps:**

```bash
# Clone repository
git clone https://github.com/yourusername/autolabmate.git
cd autolabmate

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Set production environment variables
MOCK_MODE=false
LOG_LEVEL=INFO
POSTGRES_URL=postgresql://user:pass@db:5432/autolabmate
OPENAI_API_KEY=sk-your-key

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Access application
# Frontend: http://your-server-ip:3000
# Backend: http://your-server-ip:8000/docs
```

**SSL/HTTPS Setup (with Nginx):**

```nginx
# /etc/nginx/sites-available/autolabmate
server {
    listen 80;
    server_name autolabmate.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Add SSL certificate
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/autolabmate.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/autolabmate.yourdomain.com/privkey.pem;
}
```

---

### Option 2: Vercel + Render (Serverless)

**Best for:** Cloud-native deployments, scaling to zero, cost optimization

**Frontend (Vercel):**

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Configure environment variables in Vercel dashboard:
# NEXT_PUBLIC_API_URL=https://autolabmate-api.onrender.com
```

**Backend (Render):**

1. Create new **Web Service** on Render
2. Connect GitHub repository
3. Set build command: `cd backend && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   ```
   MOCK_MODE=false
   POSTGRES_URL=[Render PostgreSQL URL]
   OPENAI_API_KEY=[Your key]
   ```

**Database (Render PostgreSQL):**
- Create PostgreSQL instance on Render
- Copy connection URL to backend environment

---

### Option 3: Kubernetes (Production)

**Best for:** Enterprise deployments, high availability

**Prerequisites:**
- Kubernetes cluster (GKE, EKS, AKS)
- kubectl configured
- Docker images pushed to registry

**1. Create Namespace:**

```bash
kubectl create namespace autolabmate
```

**2. Deploy PostgreSQL:**

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: autolabmate
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: autolabmate
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: autolabmate
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

**3. Deploy Backend:**

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: autolabmate
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
        image: your-registry/autolabmate-backend:latest
        env:
        - name: POSTGRES_URL
          value: postgresql://postgres:$(POSTGRES_PASSWORD)@postgres:5432/autolabmate
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: autolabmate
spec:
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

**4. Deploy Frontend:**

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: autolabmate
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/autolabmate-frontend:latest
        env:
        - name: NEXT_PUBLIC_API_URL
          value: http://backend
        ports:
        - containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: autolabmate
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
```

**5. Apply Deployments:**

```bash
kubectl apply -f postgres-deployment.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Check status
kubectl get pods -n autolabmate
kubectl get services -n autolabmate
```

---

## Environment Configuration

### Production Environment Variables

```bash
# AI Services
OPENAI_API_KEY=sk-production-key
OPENAI_MODEL=gpt-4

# Vector Database
PINECONE_API_KEY=production-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=autolabmate-prod

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS_PATH=/app/credentials/gcal.json
GOOGLE_CALENDAR_ID=your-calendar-id

# GitHub
GITHUB_TOKEN=ghp_production-token
GITHUB_REPO=yourorg/autolabmate-reports

# Database
POSTGRES_URL=postgresql://user:pass@host:5432/db
USE_SQLITE=false

# Application
MOCK_MODE=false
LOG_LEVEL=INFO
BACKEND_PORT=8000
FRONTEND_PORT=3000
SECRET_KEY=generate-strong-secret-key
JWT_SECRET_KEY=generate-strong-jwt-key

# Storage
UPLOAD_DIR=/app/uploads
REPORT_DIR=/app/reports
```

---

## Security Checklist

- [ ] All secrets stored in environment variables, not in code
- [ ] Strong passwords for PostgreSQL
- [ ] SSL/TLS certificates configured
- [ ] Rate limiting enabled on API
- [ ] CORS configured correctly
- [ ] File upload size limits set
- [ ] Regular backups of database
- [ ] Monitoring and alerting configured
- [ ] Security scanning in CI/CD
- [ ] Dependencies updated regularly

---

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Database health
docker-compose exec db pg_isready -U postgres
```

### Logs

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Kubernetes logs
kubectl logs -f deployment/backend -n autolabmate
kubectl logs -f deployment/frontend -n autolabmate
```

### Metrics

- **Prometheus:** Scrape metrics from `/metrics` endpoints
- **Grafana:** Visualize metrics and dashboards
- **Sentry:** Error tracking and alerting

---

## Backup & Recovery

### Database Backups

```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres autolabmate > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T postgres psql -U postgres autolabmate < backup_20240101.sql
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * docker-compose exec postgres pg_dump -U postgres autolabmate | gzip > /backups/backup_$(date +\%Y\%m\%d).sql.gz
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs service-name

# Check environment
docker-compose config

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Database Connection Issues

```bash
# Test connection
docker-compose exec backend python -c "from database.session import engine; print(engine.connect())"

# Reset database
docker-compose down -v
docker-compose up -d
```

### Port Conflicts

```bash
# Check what's using the port
lsof -i :8000
netstat -tulpn | grep 8000

# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Map host:8001 to container:8000
```

---

## Scaling

### Horizontal Scaling

**Backend:**
```bash
# Docker Compose
docker-compose up -d --scale backend=3

# Kubernetes
kubectl scale deployment backend --replicas=5 -n autolabmate
```

### Load Balancing

Use Nginx or Traefik as reverse proxy:

```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

---

## Cost Estimation

**Small Deployment (100 users/month):**
- VPS: $10-20/month
- OpenAI API: $50-100/month
- Domain: $12/year
- **Total:** ~$70-130/month

**Medium Deployment (1000 users/month):**
- Cloud VMs: $100-200/month
- Database: $50/month
- OpenAI API: $500-1000/month
- Storage: $20/month
- **Total:** ~$670-1270/month

---

## Support

- **Documentation:** Check docs/ directory
- **Issues:** GitHub Issues
- **Email:** contact@example.com

---

**Happy Deploying! 🚀**

