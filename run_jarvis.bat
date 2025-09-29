@echo off
REM ================================================================
REM Jarvis AI Assistant - Enhanced Edition Runner
REM ================================================================

title Jarvis AI Assistant - Enhanced Edition

echo.
echo 🚀 Starting Jarvis AI Assistant - Enhanced Edition
echo ================================================================
echo.

REM Check if virtual environment exists
if not exist "jarvis_env" (
    echo ❌ Virtual environment not found!
    echo Please run setup_jarvis_environment.bat first
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call jarvis_env\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    echo Please run setup_jarvis_environment.bat to fix the environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo.

REM Check for .env file
if not exist ".env" (
    echo ⚠️  Warning: .env file not found!
    echo Creating basic .env template...
    echo GOOGLE_API_KEY=your_google_api_key_here > .env
    echo LIVEKIT_URL=your_livekit_url_here >> .env
    echo LIVEKIT_API_KEY=your_livekit_api_key_here >> .env
    echo LIVEKIT_API_SECRET=your_livekit_api_secret_here >> .env
    echo.
    echo Please edit .env file and add your API keys before running again
    pause
    exit /b 1
)

REM Quick dependency check
echo 🔍 Checking critical dependencies...
python -c "
try:
    import livekit, langchain, google.generativeai
    print('✅ All critical dependencies available')
except ImportError as e:
    print('❌ Missing dependency:', e)
    print('Please run setup_jarvis_environment.bat to install dependencies')
    exit(1)
" 2>nul
if errorlevel 1 (
    echo ❌ Dependency check failed
    echo Please run setup_jarvis_environment.bat to install missing packages
    pause
    exit /b 1
)

echo.
echo 🔥 Starting Enhanced Jarvis AI Assistant...
echo ================================================================
echo 🎤 Voice interaction ready
echo 👀 Visual interface with animated eyes
echo 🧠 Advanced AI reasoning system
echo 📊 Real-time performance monitoring
echo 🛡️ Robust error handling and recovery
echo 🌍 Multi-language support (English/Hindi/Hinglish)
echo ================================================================
echo.
echo 💡 Tips:
echo - Use the visual interface to monitor performance
echo - Emergency stop button available in the GUI
echo - Press Ctrl+C to stop gracefully
echo - Check logs in the logs/ directory
echo.
echo 🚀 Launching Jarvis...
echo.

REM Run the enhanced agent
python agent.py

REM Handle exit
echo.
echo 👋 Jarvis AI Assistant has stopped
echo.
pause