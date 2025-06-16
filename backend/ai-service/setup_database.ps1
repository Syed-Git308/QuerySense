# QuerySense Phase 2: Database Setup Script
# This script sets up PostgreSQL database for QuerySense AI Service

Write-Host "🗄️  Setting up QuerySense Database..." -ForegroundColor Green
Write-Host "=" * 50

# Check if PostgreSQL is running
Write-Host "📡 Checking PostgreSQL service..." -ForegroundColor Cyan
$pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($pgService) {
    Write-Host "✅ PostgreSQL service found: $($pgService.Name) - Status: $($pgService.Status)" -ForegroundColor Green
    if ($pgService.Status -ne "Running") {
        Write-Host "🔄 Starting PostgreSQL service..." -ForegroundColor Yellow
        Start-Service $pgService.Name
    }
} else {
    Write-Host "⚠️  PostgreSQL service not found as Windows service" -ForegroundColor Yellow
}

# Try connecting with different methods
Write-Host "🔐 Attempting database connection..." -ForegroundColor Cyan

# Method 1: Try with no password (trust authentication)
Write-Host "Trying method 1: No password authentication..." -ForegroundColor Gray
$env:PGPASSWORD = ""
$result1 = & psql -U postgres -h localhost -d postgres -c "SELECT version();" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Connected successfully without password!" -ForegroundColor Green
    $connectionMethod = "no-password"
} else {
    Write-Host "❌ Method 1 failed" -ForegroundColor Red
    
    # Method 2: Try with empty password
    Write-Host "Trying method 2: Empty password..." -ForegroundColor Gray
    $env:PGPASSWORD = ""
    echo "" | & psql -U postgres -h localhost -d postgres -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Connected with empty password!" -ForegroundColor Green
        $connectionMethod = "empty-password"
    } else {
        Write-Host "❌ Method 2 failed" -ForegroundColor Red
        
        # Method 3: Provide instructions for manual setup
        Write-Host "❌ Automatic connection failed" -ForegroundColor Red
        Write-Host ""
        Write-Host "🔧 MANUAL SETUP REQUIRED:" -ForegroundColor Yellow
        Write-Host "1. During PostgreSQL installation, you set a password for 'postgres' user" -ForegroundColor White
        Write-Host "2. Please run this command manually:" -ForegroundColor White
        Write-Host "   psql -U postgres -h localhost" -ForegroundColor Cyan
        Write-Host "3. Enter the password you set during installation" -ForegroundColor White
        Write-Host "4. Then run: \i setup_database.sql" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Alternative: Reset postgres password with:" -ForegroundColor White
        Write-Host "   ALTER USER postgres PASSWORD 'newpassword';" -ForegroundColor Cyan
        
        exit 1
    }
}

Write-Host ""
Write-Host "🎉 Database setup will continue..." -ForegroundColor Green
