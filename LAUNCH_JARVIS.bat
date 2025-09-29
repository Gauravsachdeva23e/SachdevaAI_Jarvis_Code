@echo off
REM ================================================================
REM Jarvis AI Assistant - Enhanced Edition Main Launcher
REM ================================================================

title Jarvis AI Assistant - Enhanced Edition Launcher
color 0B

:main_menu
cls
echo.
echo        🤖 JARVIS AI ASSISTANT - ENHANCED EDITION 🤖
echo ================================================================
echo                    WORLD-CLASS AI ASSISTANT
echo ================================================================
echo.
echo ✨ Features: Advanced Reasoning • Multi-language • 60+ Tools
echo 📊 Monitoring: Real-time Performance • Error Recovery
echo 👀 Interface: Animated Eyes • Activity Dashboard  
echo 🎤 Voice: English • Hindi • Hinglish Support
echo.
echo ================================================================
echo                        MAIN MENU
echo ================================================================
echo.
echo  1. 🚀 START JARVIS (Quick Launch)
echo  2. ⚙️  SETUP ENVIRONMENT (First Time Setup)
echo  3. 🧪 TEST ENVIRONMENT (Verify Installation)  
echo  4. 📖 VIEW DOCUMENTATION (Setup Guide)
echo  5. 🔧 ADVANCED OPTIONS
echo  6. 🚪 EXIT
echo.
echo ================================================================

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto run_jarvis
if "%choice%"=="2" goto setup_env
if "%choice%"=="3" goto test_env
if "%choice%"=="4" goto show_docs
if "%choice%"=="5" goto advanced_menu
if "%choice%"=="6" goto exit_launcher
goto invalid_choice

:run_jarvis
cls
echo.
echo 🚀 Starting Jarvis AI Assistant...
echo ================================================================
echo.

if not exist "jarvis_env" (
    echo ❌ Environment not set up!
    echo Please run option 2 to setup the environment first.
    echo.
    pause
    goto main_menu
)

if not exist ".env" (
    echo ⚠️  Configuration file not found!
    echo Please run option 2 to setup your environment.
    echo.
    pause
    goto main_menu
)

call run_jarvis.bat
pause
goto main_menu

:setup_env
cls
echo.
echo ⚙️  Setting up Jarvis AI Assistant Environment...
echo ================================================================
echo This will install all required packages and create configuration
echo ================================================================
echo.

call setup_jarvis_environment.bat
pause
goto main_menu

:test_env
cls
echo.
echo 🧪 Testing Jarvis AI Assistant Environment...
echo ================================================================
echo.

call test_environment.bat
pause
goto main_menu

:show_docs
cls
echo.
echo 📖 Jarvis AI Assistant Documentation
echo ================================================================
echo.

if exist "README_SETUP.md" (
    echo Opening setup documentation...
    start notepad README_SETUP.md
) else (
    echo Documentation file not found!
)

if exist "AGENT_ENHANCED_README.md" (
    echo Opening agent documentation...  
    start notepad AGENT_ENHANCED_README.md
) else (
    echo Agent documentation file not found!
)

if exist "JARVIS_REASONING_IMPROVEMENTS.md" (
    echo Opening reasoning system documentation...
    start notepad JARVIS_REASONING_IMPROVEMENTS.md  
) else (
    echo Reasoning documentation file not found!
)

echo.
echo 📖 Documentation files opened in Notepad
echo.
pause
goto main_menu

:advanced_menu
cls
echo.
echo 🔧 Advanced Options
echo ================================================================
echo.
echo  1. 🧠 View Reasoning System Status
echo  2. 📊 Show Performance Metrics  
echo  3. 📁 Open Project Directory
echo  4. 📝 View Log Files
echo  5. 🔄 Reset Environment
echo  6. ⬅️  Back to Main Menu
echo.

set /p adv_choice="Enter your choice (1-6): "

if "%adv_choice%"=="1" goto show_reasoning_status
if "%adv_choice%"=="2" goto show_metrics
if "%adv_choice%"=="3" goto open_directory
if "%adv_choice%"=="4" goto view_logs
if "%adv_choice%"=="5" goto reset_env
if "%adv_choice%"=="6" goto main_menu
goto invalid_choice

:show_reasoning_status
cls
echo.
echo 🧠 Reasoning System Status
echo ================================================================
echo.

if exist "jarvis_env" (
    call jarvis_env\Scripts\activate.bat
    python -c "
from jarvis_reasoning import JarvisConfig, get_performance_metrics
import json

print('🧠 Enhanced Reasoning System Status')
print('=' * 50)

config = JarvisConfig()
print(f'AI Model: {config.model_name}')
print(f'Max Retries: {config.max_retries}')  
print(f'Timeout: {config.timeout_seconds}s')
print(f'Cache Size: {config.cache_size}')
print(f'Verbose Mode: {config.verbose_mode}')
print(f'Fallback Enabled: {config.enable_fallback}')

print()
print('📊 Performance Metrics')
print('=' * 50)
metrics = get_performance_metrics()
for key, value in metrics.items():
    if isinstance(value, float):
        print(f'{key.replace(\"_\", \" \").title()}: {value:.2f}')
    else:
        print(f'{key.replace(\"_\", \" \").title()}: {value}')
    " 2>nul || echo ❌ Could not load reasoning system status
) else (
    echo ❌ Environment not set up. Please run setup first.
)

echo.
pause
goto advanced_menu

:show_metrics
cls
echo.
echo 📊 Performance Metrics
echo ================================================================
echo.

if exist "logs" (
    echo 📁 Available log files:
    dir /b logs\*.log 2>nul || echo No log files found
    echo.
    echo 📊 Recent activity:
    if exist "logs\jarvis_agent.log" (
        echo Last 10 entries from agent log:
        powershell "Get-Content 'logs\jarvis_agent.log' | Select-Object -Last 10"
    )
) else (
    echo ❌ Logs directory not found
)

echo.
pause
goto advanced_menu

:open_directory
cls
echo.
echo 📁 Opening project directory...
start .
echo ✅ Project directory opened in File Explorer
echo.
pause
goto advanced_menu

:view_logs  
cls
echo.
echo 📝 Log Files
echo ================================================================
echo.

if exist "logs" (
    echo Available log files:
    dir logs\*.log 2>nul || echo No log files found in logs directory
    echo.
    echo Opening logs directory...
    start logs
) else (
    echo ❌ Logs directory not found
    echo Run Jarvis at least once to generate logs
)

echo.
pause
goto advanced_menu

:reset_env
cls
echo.
echo 🔄 Reset Environment
echo ================================================================
echo ⚠️  WARNING: This will delete the virtual environment
echo You will need to run setup again after this.
echo.

set /p confirm="Are you sure? (y/N): "
if /i not "%confirm%"=="y" goto advanced_menu

echo.
echo 🗑️  Removing virtual environment...
if exist "jarvis_env" (
    rmdir /s /q "jarvis_env"
    echo ✅ Virtual environment removed
) else (
    echo ⚠️  Virtual environment not found
)

echo.
echo 🗑️  Clearing temporary files...
if exist "logs" rmdir /s /q "logs" && echo ✅ Logs cleared
if exist "temp" rmdir /s /q "temp" && echo ✅ Temp files cleared
if exist "__pycache__" rmdir /s /q "__pycache__" && echo ✅ Cache cleared

echo.
echo 🔄 Environment reset complete!
echo Please run option 2 to setup the environment again.
echo.
pause
goto main_menu

:invalid_choice
cls
echo.
echo ❌ Invalid choice. Please try again.
echo.
pause
goto main_menu

:exit_launcher
cls
echo.
echo 👋 Thank you for using Jarvis AI Assistant!
echo.
echo 🎉 Your world-class AI assistant is ready when you are
echo 🚀 Run this launcher anytime to start Jarvis
echo 📖 Check the documentation for advanced features
echo.
echo ================================================================
echo        ✨ Jarvis AI Assistant - Enhanced Edition ✨
echo                    Until next time!
echo ================================================================
echo.
pause
exit /b 0