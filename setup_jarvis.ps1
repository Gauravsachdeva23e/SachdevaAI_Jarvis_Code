# ================================================================
# Jarvis AI Assistant - Enhanced Edition PowerShell Setup Script
# ================================================================

Write-Host ""
Write-Host "🚀 Jarvis AI Assistant - Enhanced Edition Setup" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "This script will set up your complete Jarvis AI environment" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator (optional but recommended)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️  Running without Administrator privileges" -ForegroundColor Yellow
    Write-Host "   Some features might require elevated permissions" -ForegroundColor Yellow
    Write-Host ""
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✅ Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python version compatibility
$versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)"
if ($versionMatch) {
    $majorVersion = [int]$matches[1]
    $minorVersion = [int]$matches[2]
    
    if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 8)) {
        Write-Host "❌ Python version $pythonVersion is too old" -ForegroundColor Red
        Write-Host "Please install Python 3.8 or newer" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Python version is compatible" -ForegroundColor Green
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "jarvis_env")) {
    Write-Host ""
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Blue
    python -m venv jarvis_env
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Virtual environment created successfully" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Blue
& "jarvis_env\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "You might need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host ""
Write-Host "📈 Upgrading pip..." -ForegroundColor Blue
python -m pip install --upgrade pip
Write-Host "✅ Pip upgraded" -ForegroundColor Green

# Install requirements
Write-Host ""
Write-Host "📦 Installing required packages..." -ForegroundColor Blue
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install requirements" -ForegroundColor Red
    Write-Host "Please check your internet connection and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ All packages installed successfully" -ForegroundColor Green

# Create necessary directories
Write-Host ""
Write-Host "📁 Creating necessary directories..." -ForegroundColor Blue
$directories = @("logs", "temp", "JarvisSandbox", "JarvisSandbox\projects", "JarvisSandbox\temp", "JarvisSandbox\scripts")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✅ Directories created" -ForegroundColor Green

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "📝 Creating .env template file..." -ForegroundColor Blue
    
    $envContent = @"
# Jarvis AI Assistant Environment Configuration
# =================================================

# Google AI API Key (Required for AI functionality)
GOOGLE_API_KEY=your_google_api_key_here

# LiveKit Configuration (Required for voice interaction)
LIVEKIT_URL=your_livekit_url_here
LIVEKIT_API_KEY=your_livekit_api_key_here
LIVEKIT_API_SECRET=your_livekit_api_secret_here

# Optional: OpenWeatherMap API Key (for weather functionality)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# System Configuration
JARVIS_LOG_LEVEL=INFO
JARVIS_CACHE_SIZE=128
JARVIS_MAX_RETRIES=3
JARVIS_TIMEOUT=30
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding utf8
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Please edit the .env file and add your API keys" -ForegroundColor Yellow
    Write-Host "   The file has been created with templates for required keys" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Run system check
Write-Host ""
Write-Host "🔍 Running system compatibility check..." -ForegroundColor Blue
$systemCheck = @"
import sys
print('✅ Python version:', sys.version)
print('✅ Python executable:', sys.executable)

# Check critical imports
modules = {
    'livekit': 'LiveKit',
    'google.generativeai': 'Google AI',
    'langchain': 'LangChain',
    'pyautogui': 'PyAutoGUI',
    'dotenv': 'Python-dotenv'
}

for module, name in modules.items():
    try:
        __import__(module)
        print(f'✅ {name} installed')
    except ImportError as e:
        print(f'❌ {name} import failed: {e}')

print('🔍 System check complete')
"@

python -c $systemCheck

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🎉 Jarvis AI Assistant Setup Complete!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit the .env file and add your API keys:" -ForegroundColor White
Write-Host "   - Google AI API Key (required for AI functionality)" -ForegroundColor Gray
Write-Host "   - LiveKit credentials (required for voice interaction)" -ForegroundColor Gray
Write-Host "   - Optional: OpenWeather API key (for weather features)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test the installation:" -ForegroundColor White
Write-Host "   .\run_jarvis.bat" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Or manually run:" -ForegroundColor White
Write-Host "   .\jarvis_env\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "   python agent.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "✨ Your enhanced Jarvis AI Assistant is ready!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue"