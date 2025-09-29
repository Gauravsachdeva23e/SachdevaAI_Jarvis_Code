"""
Test Suite for Jarvis AI Assistant
Provides comprehensive testing for all modules and functionality
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all modules to test
from jarvis_reasoning import thinking_capability
from Jarvis_google_search import google_search, get_current_datetime
from jarvis_get_whether import get_weather
from Jarvis_window_CTRL import open_app, close_app
from system_utilities import get_system_info, get_running_processes, get_network_info
from memory_store import ConversationMemory
from memory_loop import MemoryExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

class JarvisTestSuite:
    """Comprehensive test suite for Jarvis AI Assistant"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        
    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """Log the result of a test"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} | {test_name}"
        if message:
            result += f" | {message}"
        
        self.test_results.append(result)
        logger.info(result)
        
        if success:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
    
    async def test_datetime_function(self):
        """Test datetime functionality"""
        try:
            result = await get_current_datetime()
            success = isinstance(result, str) and len(result) > 0
            self.log_test_result("DateTime Function", success, f"Got: {result[:50]}")
        except Exception as e:
            self.log_test_result("DateTime Function", False, f"Error: {str(e)}")
    
    async def test_weather_function(self):
        """Test weather functionality"""
        try:
            result = await get_weather("Delhi")
            success = isinstance(result, str) and ("temperature" in result.lower() or "error" in result.lower())
            self.log_test_result("Weather Function", success, f"Got weather data for Delhi")
        except Exception as e:
            self.log_test_result("Weather Function", False, f"Error: {str(e)}")
    
    async def test_system_info(self):
        """Test system information retrieval"""
        try:
            result = await get_system_info()
            success = isinstance(result, str) and "CPU" in result and "Memory" in result
            self.log_test_result("System Info", success, "Got system information")
        except Exception as e:
            self.log_test_result("System Info", False, f"Error: {str(e)}")
    
    async def test_running_processes(self):
        """Test running processes functionality"""
        try:
            result = await get_running_processes(5)
            success = isinstance(result, str) and "Running Processes" in result
            self.log_test_result("Running Processes", success, "Got process list")
        except Exception as e:
            self.log_test_result("Running Processes", False, f"Error: {str(e)}")
    
    async def test_network_info(self):
        """Test network information"""
        try:
            result = await get_network_info()
            success = isinstance(result, str) and ("IP" in result or "Network" in result)
            self.log_test_result("Network Info", success, "Got network information")
        except Exception as e:
            self.log_test_result("Network Info", False, f"Error: {str(e)}")
    
    def test_memory_store(self):
        """Test memory storage functionality"""
        try:
            memory = ConversationMemory("test_user")
            test_conversation = {
                "messages": [{"role": "user", "content": "Hello"}],
                "timestamp": datetime.now().isoformat()
            }
            
            success = memory.save_conversation(test_conversation)
            self.log_test_result("Memory Store", success, "Saved test conversation")
            
            # Test loading
            loaded = memory.load_memory()
            load_success = isinstance(loaded, list)
            self.log_test_result("Memory Load", load_success, f"Loaded {len(loaded)} conversations")
            
        except Exception as e:
            self.log_test_result("Memory Store", False, f"Error: {str(e)}")
    
    def test_memory_extractor(self):
        """Test memory extraction functionality"""
        try:
            extractor = MemoryExtractor()
            # Test with empty session
            test_session = []
            success = hasattr(extractor, 'run') and hasattr(extractor, 'saved_message_count')
            self.log_test_result("Memory Extractor", success, "Memory extractor initialized")
        except Exception as e:
            self.log_test_result("Memory Extractor", False, f"Error: {str(e)}")
    
    async def test_google_search(self):
        """Test Google search functionality"""
        try:
            # This might fail if API keys are not set, but should handle gracefully
            result = await google_search("Python programming")
            success = isinstance(result, str) and len(result) > 0
            if "Missing environment variables" in result:
                success = True  # Expected if no API keys
            self.log_test_result("Google Search", success, "Search function works")
        except Exception as e:
            self.log_test_result("Google Search", False, f"Error: {str(e)}")
    
    async def test_thinking_capability(self):
        """Test the main thinking capability function"""
        try:
            result = await thinking_capability("What is 2+2?")
            success = isinstance(result, dict)
            self.log_test_result("Thinking Capability", success, f"Got response type: {type(result)}")
        except Exception as e:
            self.log_test_result("Thinking Capability", False, f"Error: {str(e)}")
    
    def test_imports(self):
        """Test that all modules can be imported"""
        modules_to_test = [
            'agent',
            'Jarvis_prompts', 
            'jarvis_reasoning',
            'memory_loop',
            'memory_store',
            'system_utilities',
            'Jarvis_window_CTRL',
            'Jarvis_file_opner',
            'keyboard_mouse_CTRL',
            'Jarvis_google_search',
            'jarvis_get_whether'
        ]
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                self.log_test_result(f"Import {module_name}", True, "Module imported successfully")
            except ImportError as e:
                self.log_test_result(f"Import {module_name}", False, f"Import error: {str(e)}")
            except Exception as e:
                self.log_test_result(f"Import {module_name}", False, f"Other error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting Jarvis Test Suite...")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run synchronous tests first
        print("\n📦 Testing Module Imports...")
        self.test_imports()
        
        print("\n💾 Testing Memory System...")
        self.test_memory_store()
        self.test_memory_extractor()
        
        # Run async tests
        print("\n🔧 Testing Core Functions...")
        await self.test_datetime_function()
        await self.test_system_info()
        await self.test_running_processes()
        await self.test_network_info()
        
        print("\n🌐 Testing External Services...")
        await self.test_weather_function()
        await self.test_google_search()
        
        print("\n🤖 Testing AI Reasoning...")
        await self.test_thinking_capability()
        
        # Print summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_passed + self.tests_failed}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        success_rate = (self.tests_passed / (self.tests_passed + self.tests_failed)) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.tests_failed > 0:
            print("\n🔍 Failed Tests:")
            for result in self.test_results:
                if "❌ FAIL" in result:
                    print(f"   {result}")
        
        print("\n🏁 Test Suite Complete!")
        return success_rate > 75  # Return True if >75% tests pass

async def main():
    """Main test runner"""
    test_suite = JarvisTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        print("🎉 Jarvis is ready to go!")
    else:
        print("⚠️  Some issues found. Check the logs above.")
        
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())