@echo off
REM Helm AI Production Deployment Script for Windows

setlocal enabledelayedexpansion

REM Configuration
set PROJECT_NAME=helm-ai
set ENVIRONMENT=production
set BACKUP_DIR=C:\backups\helm-ai
set LOG_FILE=C:\logs\helm-ai\deploy.log

REM Colors for output
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Logging function
:log
echo %BLUE%[%date% %time%]%NC% %1 >> "%LOG_FILE%"
echo %BLUE%[%date% %time%]%NC% %1
goto :eof

:error
echo %RED%[ERROR]%NC% %1 >> "%LOG_FILE%"
echo %RED%[ERROR]%NC% %1
exit /b 1

:success
echo %GREEN%[SUCCESS]%NC% %1 >> "%LOG_FILE%"
echo %GREEN%[SUCCESS]%NC% %1
goto :eof

:warning
echo %YELLOW%[WARNING]%NC% %1 >> "%LOG_FILE%"
echo %YELLOW%[WARNING]%NC% %1
goto :eof

REM Check prerequisites
:check_prerequisites
call :log "Checking prerequisites..."

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    call :error "Docker is not installed"
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    call :error "Docker Compose is not installed"
)

call :success "Prerequisites check completed"
goto :eof

REM Create backup
:create_backup
call :log "Creating database backup..."

set BACKUP_FILE=%BACKUP_DIR%\helm_ai_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.sql

REM Create backup directory if it doesn't exist
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

docker-compose exec -T postgres pg_dump -U helm_user helm_ai > "%BACKUP_FILE%"

if %errorlevel% equ 0 (
    call :success "Database backup created: %BACKUP_FILE%"
) else (
    call :error "Failed to create database backup"
)
goto :eof

REM Pull latest images
:pull_images
call :log "Pulling latest Docker images..."

docker-compose pull

if %errorlevel% equ 0 (
    call :success "Docker images pulled successfully"
) else (
    call :error "Failed to pull Docker images"
)
goto :eof

REM Run database migrations
:run_migrations
call :log "Running database migrations..."

docker-compose run --rm helm-ai python -m alembic upgrade head

if %errorlevel% equ 0 (
    call :success "Database migrations completed successfully"
) else (
    call :error "Database migrations failed"
)
goto :eof

REM Deploy application
:deploy_application
call :log "Deploying Helm AI application..."

REM Stop existing services
call :log "Stopping existing services..."
docker-compose down

REM Start new services
call :log "Starting new services..."
docker-compose up -d

REM Wait for services to be ready
call :log "Waiting for services to be ready..."
timeout /t 30 /nobreak >nul

REM Check service health
call :check_health

call :success "Application deployed successfully"
goto :eof

REM Check service health
:check_health
call :log "Checking service health..."

REM Check main application
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    call :success "Main application is healthy"
) else (
    call :error "Main application health check failed"
)

REM Check database
docker-compose exec -T postgres pg_isready -U helm_user >nul 2>&1
if %errorlevel% equ 0 (
    call :success "Database is healthy"
) else (
    call :error "Database health check failed"
)

REM Check Redis
docker-compose exec -T redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    call :success "Redis is healthy"
) else (
    call :error "Redis health check failed"
)
goto :eof

REM Cleanup old images
:cleanup
call :log "Cleaning up old Docker images..."

REM Remove unused images
docker image prune -f

call :success "Cleanup completed"
goto :eof

REM Show logs
:show_logs
call :log "Showing application logs..."
docker-compose logs -f helm-ai
goto :eof

REM Main deployment function
:main
call :log "Starting Helm AI deployment to %ENVIRONMENT%..."

call :check_prerequisites

if "%1"=="" set "action=deploy"
if "%1"=="deploy" set "action=deploy"
if "%1"=="rollback" set "action=rollback"
if "%1"=="logs" set "action=logs"
if "%1"=="backup" set "action=backup"
if "%1"=="health" set "action=health"

if "%action%"=="deploy" (
    call :create_backup
    call :pull_images
    call :run_migrations
    call :deploy_application
    call :cleanup
) else if "%action%"=="rollback" (
    call :log "Rollback functionality not implemented in Windows script"
) else if "%action%"=="logs" (
    call :show_logs
) else if "%action%"=="backup" (
    call :create_backup
) else if "%action%"=="health" (
    call :check_health
) else (
    echo Usage: %0 {deploy^|rollback^|logs^|backup^|health}
    exit /b 1
)

call :log "Deployment process completed successfully!"
goto :eof

REM Run main function with all arguments
call :main %*
