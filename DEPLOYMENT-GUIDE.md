# Helm AI Deployment Guide

This guide covers the complete deployment process for Helm AI, including Docker setup, CI/CD pipeline, and monitoring.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Environment Configuration](#environment-configuration)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Health Checks & Monitoring](#health-checks--monitoring)
6. [Deployment Scripts](#deployment-scripts)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- Docker 20.10+ and Docker Compose 2.0+
- Python 3.9+ (for local development)
- PostgreSQL 15+ (for production)
- Redis 7+ (for production)
- 4GB+ RAM minimum
- 20GB+ disk space minimum

### Required Software

- Docker Desktop (for local development)
- Git
- kubectl (for Kubernetes deployment)
- AWS CLI (if using AWS services)

## Docker Deployment

### Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/helm-ai.git
   cd helm-ai
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development environment:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Run database migrations:**
   ```bash
   docker-compose run --rm helm-ai python -m alembic upgrade head
   ```

### Production Environment

1. **Prepare production environment:**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Generate SSL certificates:**
   ```bash
   mkdir -p deployment/ssl
   # Generate self-signed cert for testing or use Let's Encrypt for production
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout deployment/ssl/key.pem -out deployment/ssl/cert.pem
   ```

3. **Deploy application:**
   ```bash
   # Linux/macOS
   ./scripts/deploy.sh deploy
   
   # Windows
   scripts\deploy.bat deploy
   ```

4. **Verify deployment:**
   ```bash
   curl http://localhost:8000/health
   ```

## Environment Configuration

### Key Environment Variables

#### Database Configuration
```bash
DATABASE_URL=postgresql://helm_user:helm_password@localhost:5432/helm_ai
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
```

#### Redis Configuration
```bash
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your-redis-password
```

#### Security Configuration
```bash
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key
ENABLE_RATE_LIMITING=true
```

#### AWS Configuration
```bash
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET=helm-ai-storage
```

### Environment-Specific Settings

#### Development
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_RATE_LIMITING=false
```

#### Production
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
ENABLE_RATE_LIMITING=true
```

## CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline includes:

1. **Code Quality Checks**
   - Linting (flake8, black, isort)
   - Type checking (mypy)
   - Security scanning (bandit, safety)

2. **Testing**
   - Unit tests
   - Integration tests
   - Performance tests
   - Code coverage reporting

3. **Security Scanning**
   - Trivy vulnerability scanner
   - Dependency scanning

4. **Build & Deploy**
   - Docker image building
   - Multi-architecture support
   - Registry push
   - Automated deployment

### Pipeline Triggers

- **Push to `main`**: Full pipeline with deployment to staging
- **Pull Request**: Full pipeline without deployment
- **Release**: Full pipeline with deployment to production
- **Push to `develop`**: Build and deploy to staging

### Environment-Specific Pipelines

#### Staging Environment
- Triggered by pushes to `develop` branch
- Runs all tests and security scans
- Deploys to staging environment
- Includes performance testing

#### Production Environment
- Triggered by GitHub releases
- Runs full validation pipeline
- Deploys to production environment
- Includes rollback capabilities

## Health Checks & Monitoring

### Health Check Endpoints

#### Basic Health Check
```
GET /health
```
Returns basic application status.

#### Detailed Health Check
```
GET /health/detailed
```
Returns comprehensive health status including:
- System resources
- Database connectivity
- Redis connectivity
- External services status
- Application metrics

#### Kubernetes Probes
```
GET /health/readiness
GET /health/liveness
```
Kubernetes readiness and liveness probes.

### Monitoring Stack

#### Prometheus Metrics
```
GET /metrics
```
Returns application metrics in Prometheus format.

#### Grafana Dashboard
- Available at `http://localhost:3000`
- Pre-configured dashboards for:
  - Application performance
  - Database metrics
  - System resources
  - Error rates

#### Log Aggregation
- Structured logging with ELK stack
- Centralized log collection
- Real-time log analysis

## Deployment Scripts

### Linux/macOS Script (`scripts/deploy.sh`)

**Usage:**
```bash
./scripts/deploy.sh [deploy|rollback|logs|backup|health]
```

**Features:**
- Automated backup creation
- Database migrations
- Service health checks
- Rollback functionality
- Comprehensive logging

### Windows Script (`scripts/deploy.bat`)

**Usage:**
```cmd
scripts\deploy.bat [deploy|rollback|logs|backup|health]
```

**Features:**
- Windows-compatible deployment
- Color-coded output
- Error handling
- Progress tracking

### Docker Compose Commands

#### Development
```bash
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml logs -f helm-ai
docker-compose -f docker-compose.dev.yml down
```

#### Production
```bash
docker-compose up -d
docker-compose logs -f helm-ai
docker-compose down
docker-compose pull
```

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check database status
docker-compose exec postgres pg_isready -U helm_user

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### Redis Connection Errors
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis

# Flush Redis cache
docker-compose exec redis redis-cli flushall
```

#### Application Startup Issues
```bash
# Check application logs
docker-compose logs helm-ai

# Check health status
curl http://localhost:8000/health

# Restart services
docker-compose restart helm-ai
```

#### Performance Issues
```bash
# Check system resources
docker stats

# Monitor application metrics
curl http://localhost:8000/metrics

# Check slow queries
docker-compose logs helm-ai | grep "slow"
```

### Debugging Tips

1. **Enable Debug Mode:**
   ```bash
   DEBUG=true docker-compose up -d helm-ai
   ```

2. **Check Logs:**
   ```bash
   docker-compose logs -f helm-ai
   ```

3. **Access Container Shell:**
   ```bash
   docker-compose exec helm-ai bash
   ```

4. **Verify Environment Variables:**
   ```bash
   docker-compose exec helm-ai env | grep -E "DATABASE_URL|REDIS_URL|SECRET_KEY"
   ```

### Performance Optimization

#### Database Optimization
```bash
# Check database connections
docker-compose exec postgres psql -U helm_user -c "SELECT count(*) FROM pg_stat_activity;"

# Optimize PostgreSQL settings
# Edit docker-compose.yml to adjust memory and connection settings
```

#### Redis Optimization
```bash
# Check Redis memory usage
docker-compose exec redis redis-cli info memory

# Optimize Redis settings
# Edit docker-compose.yml to adjust memory limits
```

#### Application Optimization
```bash
# Monitor CPU and memory usage
docker stats helm-ai

# Adjust worker processes
# Edit docker-compose.yml to scale services
```

## Security Considerations

### SSL/TLS Configuration
- Use HTTPS in production
- Implement proper certificate management
- Configure secure headers

### Environment Variables
- Never commit secrets to version control
- Use environment-specific configuration files
- Implement proper secret management

### Network Security
- Use private networks in Docker Compose
- Implement proper firewall rules
- Configure rate limiting

### Access Control
- Implement proper authentication
- Use role-based access control
- Regular security audits

## Backup and Recovery

### Database Backups
```bash
# Manual backup
docker-compose exec -T postgres pg_dump -U helm_user helm_ai > backup.sql

# Automated backup
./scripts/deploy.sh backup
```

### Application Backups
```bash
# Backup application data
docker run --rm -v $(pwd)/data:/backup helm-ai tar czf /backup/helm-ai_backup_$(date +%Y%m%d).tar.gz /app/data
```

### Disaster Recovery
```bash
# Restore database
docker-compose exec -T postgres psql -U helm_user helm_ai < backup.sql

# Restore application
docker run --rm -v $(pwd)/backup:/backup helm-ai tar xzf /backup/helm_ai_backup_20231201_120000.tar.gz -C /app
```

## Maintenance

### Regular Tasks
- Update dependencies
- Apply security patches
- Clean up old Docker images
- Monitor disk space
- Review logs for issues

### Monitoring
- Set up alerting for critical services
- Monitor performance metrics
- Track error rates
- Review security logs

### Updates
- Update Docker images regularly
- Apply security patches promptly
- Test updates in staging first
- Document all changes

## Support

For deployment issues:
1. Check the logs for error messages
2. Verify environment configuration
3. Consult this troubleshooting guide
4. Review the GitHub Issues
5. Contact the development team

For application issues:
1. Check the health check endpoints
2. Review application logs
3. Verify database connectivity
4. Check external service status
5. Monitor performance metrics

---

**Last Updated:** December 2023
**Version:** 1.0.0
**Maintainer:** Helm AI Team
