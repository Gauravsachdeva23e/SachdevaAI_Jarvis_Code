@echo off
REM ================================================================
REM Jarvis AI Assistant - Enhanced Edition Setup Script
REM ================================================================
echo.
echo 🚀 Jarvis AI Assistant - Enhanced Edition Setup
echo ================================================================
echo This script will set up your complete Jarvis AI environment
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python is installed
python --version

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo 📍 Python version: %python_version%

REM Create virtual environment if it doesn't exist
if not exist "jarvis_env" (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv jarvis_env
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created successfully
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo.
echo 🔄 Activating virtual environment...
call jarvis_env\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated

REM Upgrade pip
echo.
echo 📈 Upgrading pip...
python -m pip install --upgrade pip
echo ✅ Pip upgraded

REM Install requirements
echo.
echo 📦 Installing required packages...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo ✅ All packages installed successfully

REM Create necessary directories
echo.
echo 📁 Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp
if not exist "JarvisSandbox" mkdir JarvisSandbox
if not exist "JarvisSandbox\projects" mkdir JarvisSandbox\projects
if not exist "JarvisSandbox\temp" mkdir JarvisSandbox\temp
if not exist "JarvisSandbox\scripts" mkdir JarvisSandbox\scripts
echo ✅ Directories created

REM Check for .env file
if not exist ".env" (
    echo.
    echo 📝 Creating .env template file...
    echo # Jarvis AI Assistant Environment Configuration > .env
    echo # ================================================= >> .env
    echo. >> .env
    echo # Google AI API Key (Required for AI functionality) >> .env
    echo GOOGLE_API_KEY=your_google_api_key_here >> .env
    echo. >> .env
    echo # LiveKit Configuration (Required for voice interaction) >> .env
    echo LIVEKIT_URL=your_livekit_url_here >> .env
    echo LIVEKIT_API_KEY=your_livekit_api_key_here >> .env
    echo LIVEKIT_API_SECRET=your_livekit_api_secret_here >> .env
    echo. >> .env
    echo # Optional: OpenWeatherMap API Key (for weather functionality) >> .env
    echo OPENWEATHER_API_KEY=your_openweather_api_key_here >> .env
    echo. >> .env
    echo # System Configuration >> .env
    echo JARVIS_LOG_LEVEL=INFO >> .env
    echo JARVIS_CACHE_SIZE=128 >> .env
    echo JARVIS_MAX_RETRIES=3 >> .env
    echo JARVIS_TIMEOUT=30 >> .env
    echo.
    echo ⚠️  IMPORTANT: Please edit the .env file and add your API keys
    echo    The file has been created with templates for required keys
) else (
    echo ✅ .env file already exists
)

REM Run system check
echo.
echo 🔍 Running system compatibility check...
python -c "
import sys
print('✅ Python version:', sys.version)
print('✅ Python executable:', sys.executable)

# Check critical imports
try:
    import livekit
    print('✅ LiveKit installed')
except ImportError as e:
    print('❌ LiveKit import failed:', e)

try:
    import google.generativeai
    print('✅ Google AI installed')
except ImportError as e:
    print('❌ Google AI import failed:', e)

try:
    import langchain
    print('✅ LangChain installed')
except ImportError as e:
    print('❌ LangChain import failed:', e)

try:
    import pyautogui
    print('✅ PyAutoGUI installed')
except ImportError as e:
    print('❌ PyAutoGUI import failed:', e)

try:
    import dotenv
    print('✅ Python-dotenv installed')
except ImportError as e:
    print('❌ Python-dotenv import failed:', e)

print('🔍 System check complete')
"

echo.
echo ================================================================
echo 🎉 Jarvis AI Assistant Setup Complete!
echo ================================================================
echo.
echo 📋 Next Steps:
echo 1. Edit the .env file and add your API keys:
echo    - Google AI API Key (required for AI functionality)
echo    - LiveKit credentials (required for voice interaction)
echo    - Optional: OpenWeather API key (for weather features)
echo.
echo 2. Test the installation:
echo    run_jarvis.bat
echo.
echo 3. Or manually run:
echo    jarvis_env\Scripts\activate
echo    python agent.py
echo.
echo ================================================================
echo ✨ Your enhanced Jarvis AI Assistant is ready!
echo ================================================================
echo.
pause