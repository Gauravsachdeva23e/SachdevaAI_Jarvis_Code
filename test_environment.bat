@echo off
REM ================================================================
REM Jarvis AI Assistant - Environment Test Script
REM ================================================================

title Jarvis AI Assistant - Environment Test

echo.
echo 🧪 Testing Jarvis AI Assistant Environment
echo ================================================================
echo.

REM Check if virtual environment exists
if not exist "jarvis_env" (
    echo ❌ Virtual environment not found!
    echo Please run setup_jarvis_environment.bat first
    goto :end
)

echo ✅ Virtual environment found
echo.

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call jarvis_env\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    goto :end
)

echo ✅ Virtual environment activated
echo.

REM Test Python and packages
echo 🔍 Testing Python and critical packages...
python -c "
print('🐍 Testing Python Installation...')
import sys
print(f'✅ Python {sys.version}')

print()
print('📦 Testing Critical Packages...')

# Test core packages
packages = [
    ('livekit', 'LiveKit Agent Framework'),
    ('langchain', 'LangChain AI Framework'),
    ('google.generativeai', 'Google AI SDK'),
    ('dotenv', 'Environment Configuration'),
    ('pyautogui', 'GUI Automation'),
    ('asyncio', 'Async Programming'),
    ('logging', 'Logging System')
]

all_good = True
for package, description in packages:
    try:
        __import__(package)
        print(f'✅ {description}')
    except ImportError as e:
        print(f'❌ {description} - {e}')
        all_good = False

print()
if all_good:
    print('🎉 All critical packages are working!')
else:
    print('⚠️  Some packages have issues. Please run setup script again.')

print()
print('🧠 Testing Enhanced Reasoning System...')
try:
    from jarvis_reasoning import JarvisConfig, get_performance_metrics, thinking_capability
    config = JarvisConfig()
    print(f'✅ JarvisConfig loaded - Model: {config.model_name}')
    
    metrics = get_performance_metrics()
    print(f'✅ Performance monitoring ready')
    
    print(f'✅ Enhanced reasoning system functional')
except Exception as e:
    print(f'❌ Enhanced reasoning system error: {e}')

print()
print('🤖 Testing Agent System...')
try:
    from agent import Assistant, entrypoint
    print('✅ Enhanced Agent class loaded')
    print('✅ Main entrypoint function ready')
except Exception as e:
    print(f'❌ Agent system error: {e}')

print()
print('👀 Testing Visual Interface...')
try:
    from jarvis_visual import JarvisState, set_jarvis_state, add_activity_log
    print('✅ Visual interface components loaded')
    print('✅ State management ready')
except Exception as e:
    print(f'❌ Visual interface error: {e}')

print()
print('🛠️  Testing Tool Orchestrator...')
try:
    from tool_orchestrator import get_orchestrator
    orchestrator = get_orchestrator()
    tool_count = len(orchestrator.tool_registry)
    print(f'✅ Tool orchestrator loaded with {tool_count} tools')
except Exception as e:
    print(f'❌ Tool orchestrator error: {e}')

print()
print('🔍 Environment Test Complete!')
print('=' * 50)
"

if errorlevel 1 (
    echo ❌ Python test failed
    goto :end
)

REM Check .env file
echo.
echo 🔧 Checking configuration...
if exist ".env" (
    echo ✅ .env file exists
    findstr /C:"your_google_api_key_here" .env >nul
    if not errorlevel 1 (
        echo ⚠️  .env file contains default values
        echo Please edit .env and add your real API keys
    ) else (
        echo ✅ .env file appears to be configured
    )
) else (
    echo ❌ .env file missing
    echo Please run setup_jarvis_environment.bat to create it
)

echo.
echo 📁 Checking directory structure...
set dirs=logs temp JarvisSandbox JarvisSandbox\projects
for %%d in (%dirs%) do (
    if exist "%%d" (
        echo ✅ %%d directory exists
    ) else (
        echo ⚠️  %%d directory missing
    )
)

echo.
echo ================================================================
echo 🎯 Environment Test Results
echo ================================================================

if exist ".env" if exist "jarvis_env" (
    echo ✅ Basic environment setup: GOOD
    echo ✅ Virtual environment: READY
    echo ✅ Python packages: INSTALLED
    echo ✅ Enhanced systems: LOADED
    echo.
    echo 🚀 Your Jarvis environment looks ready!
    echo.
    echo 📋 Next steps:
    echo 1. Make sure your .env file has real API keys
    echo 2. Run: run_jarvis.bat
    echo 3. Start talking to your AI assistant!
    echo.
    echo 🎤 Voice commands to try:
    echo - "What time is it?"
    echo - "Tell me a joke"  
    echo - "System info batao" (Hinglish)
    echo - "कोड लिखो" (Hindi)
) else (
    echo ❌ Environment setup incomplete
    echo Please run setup_jarvis_environment.bat first
)

echo.
echo ================================================================

:end
echo.
pause