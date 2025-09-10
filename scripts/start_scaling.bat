@echo off
REM Script to start horizontal scaling setup on Windows

echo 🚀 Starting CampusHub360 Horizontal Scaling Setup
echo ==================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "docker-compose.scaling.yml" (
    echo ❌ docker-compose.scaling.yml not found
    pause
    exit /b 1
)

if not exist "nginx.conf" (
    echo ❌ nginx.conf not found
    pause
    exit /b 1
)

if not exist "gunicorn.conf.py" (
    echo ❌ gunicorn.conf.py not found
    pause
    exit /b 1
)

echo ✅ All required files found

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose -f docker-compose.scaling.yml down

REM Build and start services
echo 🔨 Building and starting services...
docker-compose -f docker-compose.scaling.yml up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check service health
echo 🏥 Checking service health...

REM Check Django instances
for %%p in (8000 8001 8002 8003) do (
    curl -f http://localhost:%%p/health/ >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Django instance on port %%p is healthy
    ) else (
        echo ❌ Django instance on port %%p is not responding
    )
)

REM Check Redis
docker exec campushub_redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis is healthy
) else (
    echo ❌ Redis is not responding
)

REM Check PostgreSQL
docker exec campushub_postgres pg_isready -U campushub -d campushub360 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL is healthy
) else (
    echo ❌ PostgreSQL is not responding
)

REM Check NGINX
curl -f http://localhost/health/ >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ NGINX load balancer is healthy
) else (
    echo ❌ NGINX load balancer is not responding
)

echo.
echo 🎉 Horizontal scaling setup complete!
echo ==================================================
echo 📊 Services running:
echo    • NGINX Load Balancer: http://localhost
echo    • Django Instance 1: http://localhost:8000
echo    • Django Instance 2: http://localhost:8001
echo    • Django Instance 3: http://localhost:8002
echo    • Django Instance 4: http://localhost:8003
echo    • Redis Cache: localhost:6379
echo    • PostgreSQL DB: localhost:5432
echo    • Redis Commander: http://localhost:8081
echo.
echo 🧪 Test the setup:
echo    curl http://localhost/health/
echo    curl http://localhost/api/health/
echo.
echo 📈 Expected performance:
echo    • 4x Django instances
echo    • Load balanced requests
echo    • Redis caching
echo    • Target: 5,000+ RPS
echo.
echo 🛑 To stop: docker-compose -f docker-compose.scaling.yml down
pause
