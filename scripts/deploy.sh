#!/bin/bash

# 🚀 SHADOW.AI II - Deployment Script
# Automated deployment for different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT=${1:-development}

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate environment
validate_environment() {
    case $ENVIRONMENT in
        development|staging|production)
            log_info "Deploying to $ENVIRONMENT environment"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT"
            log_error "Valid environments: development, staging, production"
            exit 1
            ;;
    esac
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if environment file exists
    ENV_FILE="$PROJECT_ROOT/environments/$ENVIRONMENT.env"
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file not found: $ENV_FILE"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Backup current deployment
backup_deployment() {
    log_info "Creating backup..."
    
    BACKUP_DIR="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database if running
    if docker-compose ps | grep -q postgres; then
        log_info "Backing up database..."
        docker-compose exec -T postgres pg_dump -U trader shadow_ai > "$BACKUP_DIR/database.sql"
    fi
    
    # Backup volumes
    docker run --rm -v shadow-ai_postgres-data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/postgres-data.tar.gz -C /data .
    docker run --rm -v shadow-ai_redis-data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/redis-data.tar.gz -C /data .
    
    log_success "Backup created at $BACKUP_DIR"
}

# Deploy services
deploy_services() {
    log_info "Deploying services..."
    
    cd "$PROJECT_ROOT"
    
    # Copy environment file
    cp "environments/$ENVIRONMENT.env" .env
    
    # Build and start services
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Building production images..."
        docker-compose build --parallel
    fi
    
    log_info "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    log_success "Services deployed"
}

# Health check
health_check() {
    log_info "Running health checks..."
    
    # Check API Gateway
    if curl -s -f http://localhost/health > /dev/null; then
        log_success "API Gateway is healthy"
    else
        log_warning "API Gateway health check failed"
    fi
    
    # Check Dashboard
    if curl -s -f http://localhost:3000/api/health > /dev/null; then
        log_success "Dashboard is healthy"
    else
        log_warning "Dashboard health check failed"
    fi
    
    # Check MCP Server
    if curl -s -f http://localhost:8000/health > /dev/null; then
        log_success "MCP Server is healthy"
    else
        log_warning "MCP Server health check failed"
    fi
    
    # Check Database
    if docker-compose exec -T postgres pg_isready -U trader -d shadow_ai > /dev/null; then
        log_success "Database is healthy"
    else
        log_warning "Database health check failed"
    fi
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    if docker-compose exec -T dashboard npx prisma migrate deploy; then
        log_success "Database migrations completed"
    else
        log_warning "Database migrations failed"
    fi
}

# Display deployment info
display_info() {
    log_success "Deployment completed!"
    echo ""
    echo "🌐 SHADOW.AI II - $ENVIRONMENT Environment"
    echo "=========================================="
    echo "📊 Dashboard: http://localhost:3000"
    echo "🤖 MCP Server: http://localhost:8000"
    echo "📈 Grafana: http://localhost:3001"
    echo "📊 Prometheus: http://localhost:9090"
    echo ""
    echo "Useful commands:"
    echo "  make logs          - View all logs"
    echo "  make health        - Check service health"
    echo "  make status        - Show service status"
    echo ""
}

# Main deployment function
main() {
    log_info "Starting deployment to $ENVIRONMENT environment..."
    
    validate_environment
    check_prerequisites
    
    if [ "$ENVIRONMENT" = "production" ]; then
        backup_deployment
    fi
    
    deploy_services
    run_migrations
    health_check
    display_info
}

# Run main function
main "$@"





