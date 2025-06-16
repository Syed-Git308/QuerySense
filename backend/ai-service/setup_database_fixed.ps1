# QuerySense Phase 2: Database Setup Script
# This script sets up PostgreSQL database for QuerySense AI service

Write-Host "🗄️  QuerySense Database Setup" -ForegroundColor Green
Write-Host "=" * 50

# Test connection methods
Write-Host "Testing PostgreSQL connection..." -ForegroundColor Cyan

# Method 1: Try without password
try {
    $result = psql -U postgres -h localhost -d postgres -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Connected successfully without password!" -ForegroundColor Green
        $connectionMethod = "no-password"
    }
} catch {
    # Method 2: Try with empty password
    try {
        $result = cmd /c "echo. | psql -U postgres -h localhost -d postgres -c ""SELECT version();""" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Connected with empty password!" -ForegroundColor Green
            $connectionMethod = "empty-password"
        }
    } catch {
        Write-Host "❌ Cannot connect to PostgreSQL" -ForegroundColor Red
        Write-Host "Please check if PostgreSQL is running and accessible" -ForegroundColor Yellow
        Write-Host "You may need to:" -ForegroundColor Yellow
        Write-Host "1. Set a password for postgres user" -ForegroundColor Gray
        Write-Host "2. Modify pg_hba.conf for local connections" -ForegroundColor Gray
        Write-Host "3. Restart PostgreSQL service" -ForegroundColor Gray
        exit 1
    }
}

Write-Host ""
Write-Host "Creating QuerySense database and user..." -ForegroundColor Cyan

# Create database and user
$sql = @"
-- Create user if not exists
DO `$`$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'querysense') THEN
        CREATE USER querysense WITH PASSWORD 'querysense123';
    END IF;
END
`$`$;

-- Create database if not exists
SELECT 'CREATE DATABASE querysense_ai OWNER querysense'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'querysense_ai')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE querysense_ai TO querysense;
"@

try {
    $sql | psql -U postgres -h localhost -d postgres
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database and user created successfully!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed to create database" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Installing pgvector extension..." -ForegroundColor Cyan

$vectorSql = @"
-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
"@

try {
    $vectorSql | psql -U postgres -h localhost -d querysense_ai
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pgvector extension installed!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  pgvector extension not available - will install later" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Database setup complete!" -ForegroundColor Green
Write-Host "Database: querysense_ai" -ForegroundColor White
Write-Host "User: querysense" -ForegroundColor White
Write-Host "Password: querysense123" -ForegroundColor White
