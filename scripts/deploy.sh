#!/bin/bash
# Helm AI Production Deployment Script

set -euo pipefail

# Configuration
PROJECT_NAME="helm-ai"
DOCKER_REGISTRY="ghcr.io/your-org"
ENVIRONMENT="production"
BACKUP_DIR="/backups"
LOG_FILE="/var/log/helm-ai/deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root"
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check if kubectl is installed (for Kubernetes deployment)
    if ! command -v kubectl &> /dev/null; then
        warning "kubectl is not installed - Kubernetes deployment will not work"
    fi
    
    success "Prerequisites check completed"
}

# Create backup
create_backup() {
    log "Creating database backup..."
    
    BACKUP_FILE="$BACKUP_DIR/helm_ai_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    docker-compose exec -T postgres pg_dump -U helm_user helm_ai > "$BACKUP_FILE"
    
    if [[ $? -eq 0 ]]; then
        success "Database backup created: $BACKUP_FILE"
    else
        error "Failed to create database backup"
    fi
}

# Pull latest images
pull_images() {
    log "Pulling latest Docker images..."
    
    docker-compose pull
    
    if [[ $? -eq 0 ]]; then
        success "Docker images pulled successfully"
    else
        error "Failed to pull Docker images"
    fi
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    docker-compose run --rm helm-ai python -m alembic upgrade head
    
    if [[ $? -eq 0 ]]; then
        success "Database migrations completed successfully"
    else
        error "Database migrations failed"
    fi
}

# Deploy application
deploy_application() {
    log "Deploying Helm AI application..."
    
    # Stop existing services
    log "Stopping existing services..."
    docker-compose down
    
    # Start new services
    log "Starting new services..."
    docker-compose up -d
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_health
    
    success "Application deployed successfully"
}

# Check service health
check_health() {
    log "Checking service health..."
    
    # Check main application
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Main application is healthy"
    else
        error "Main application health check failed"
    fi
    
    # Check database
    if docker-compose exec -T postgres pg_isready -U helm_user > /dev/null 2>&1; then
        success "Database is healthy"
    else
        error "Database health check failed"
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        success "Redis is healthy"
    else
        error "Redis health check failed"
    fi
}

# Rollback deployment
rollback() {
    log "Rolling back deployment..."
    
    # Get previous image tag
    PREVIOUS_TAG=$(docker images --format "table {{.Repository}}:{{.Tag}}" | grep "$PROJECT_NAME" | tail -2 | head -1)
    
    if [[ -z "$PREVIOUS_TAG" ]]; then
        error "No previous image found for rollback"
    fi
    
    log "Rolling back to: $PREVIOUS_TAG"
    
    # Update docker-compose to use previous image
    sed -i "s|image: $PROJECT_NAME:latest|image: $PREVIOUS_TAG|g" docker-compose.yml
    
    # Redeploy
    deploy_application
    
    success "Rollback completed successfully"
}

# Cleanup old images
cleanup() {
    log "Cleaning up old Docker images..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove old images (keep last 5)
    docker images --format "table {{.Repository}}:{{.Tag}}" | grep "$PROJECT_NAME" | tail -n +6 | awk '{print $1":"$2}' | xargs -r docker rmi
    
    success "Cleanup completed"
}

# Show logs
show_logs() {
    log "Showing application logs..."
    docker-compose logs -f helm-ai
}

# Main deployment function
main() {
    log "Starting Helm AI deployment to $ENVIRONMENT..."
    
    check_root
    check_prerequisites
    
    case "${1:-deploy}" in
        "deploy")
            create_backup
            pull_images
            run_migrations
            deploy_application
            cleanup
            ;;
        "rollback")
            rollback
            ;;
        "logs")
            show_logs
            ;;
        "backup")
            create_backup
            ;;
        "health")
            check_health
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|logs|backup|health}"
            exit 1
            ;;
    esac
    
    log "Deployment process completed successfully!"
}

# Trap signals for cleanup
trap 'error "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@"
