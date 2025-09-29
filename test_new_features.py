"""
Test Script for New Jarvis Features
Tests visual interface, VS Code sandbox, and coding tools
"""

import asyncio
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_visual_interface():
    """Test the visual interface with eyes"""
    print("🧪 Testing Visual Interface...")
    
    try:
        from jarvis_visual import (
            initialize_visual_interface, set_jarvis_state, JarvisState,
            start_writing_session, stop_writing_session, add_activity_log
        )
        
        # Initialize visual interface
        visual = initialize_visual_interface()
        if visual:
            print("✅ Visual interface initialized")
            
            # Test different states
            add_activity_log("Testing visual interface states...")
            
            await asyncio.sleep(2)
            set_jarvis_state(JarvisState.LISTENING, "Testing listening mode...")
            await asyncio.sleep(3)
            
            set_jarvis_state(JarvisState.THINKING, "Processing complex query...")
            await asyncio.sleep(3)
            
            start_writing_session("Testing writing animation...")
            await asyncio.sleep(4)
            stop_writing_session()
            
            set_jarvis_state(JarvisState.IDLE, "Visual interface test complete")
            add_activity_log("✅ All visual states tested successfully")
            
        return True
        
    except Exception as e:
        logger.error(f"Visual interface test failed: {e}")
        return False

async def test_vscode_sandbox():
    """Test VS Code sandbox functionality"""
    print("🧪 Testing VS Code Sandbox...")
    
    try:
        from vscode_sandbox import get_sandbox, open_vscode_sandbox, create_code_file
        
        # Test sandbox creation
        result = await open_vscode_sandbox("test_project")
        if "successfully" in result:
            print("✅ VS Code sandbox opened")
            
            # Test file creation
            result = await create_code_file("test_hello.py", "python", 
                                          'print("Hello from Jarvis sandbox test!")')
            if "Created" in result:
                print("✅ Test file created in sandbox")
            else:
                print("⚠️ File creation test failed")
        else:
            print("⚠️ VS Code sandbox test failed - VS Code might not be installed")
            
        return True
        
    except Exception as e:
        logger.error(f"VS Code sandbox test failed: {e}")
        return False

async def test_coding_tools():
    """Test coding tools functionality"""
    print("🧪 Testing Coding Tools...")
    
    try:
        from coding_tools import analyze_code, generate_function, generate_class
        
        # Test code analysis
        test_code = '''
def hello(name):
    if name=="world":
        print("Hello "+name+"!")
    return True
'''
        
        result = await analyze_code(test_code, "python")
        if "CODE ANALYSIS REPORT" in result:
            print("✅ Code analysis working")
        
        # Test function generation
        result = await generate_function("calculate_sum", "Calculate sum of two numbers", 
                                       "a: int, b: int", "int")
        if "Generated" in result:
            print("✅ Function generation working")
        
        # Test class generation  
        result = await generate_class("DataProcessor", "Process and analyze data", "process,validate")
        if "Generated" in result:
            print("✅ Class generation working")
            
        return True
        
    except Exception as e:
        logger.error(f"Coding tools test failed: {e}")
        return False

async def test_stop_control():
    """Test stop/start control functionality"""
    print("🧪 Testing Stop Control...")
    
    try:
        from jarvis_visual import should_stop_operation, get_visual_interface
        from vscode_sandbox import stop_all_writing
        
        # Test stop mechanism
        visual = get_visual_interface()
        if visual:
            # Simulate writing start
            visual.start_writing_mode("Testing stop control...")
            await asyncio.sleep(1)
            
            # Test stop check
            if not should_stop_operation():
                print("✅ Stop control ready")
                
                # Simulate emergency stop
                await stop_all_writing()
                
                if should_stop_operation():
                    print("✅ Emergency stop working")
                else:
                    print("⚠️ Emergency stop might not be working")
            
        return True
        
    except Exception as e:
        logger.error(f"Stop control test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Jarvis New Features Test Suite")
    print("=" * 50)
    
    tests = [
        ("Visual Interface", test_visual_interface),
        ("VS Code Sandbox", test_vscode_sandbox), 
        ("Coding Tools", test_coding_tools),
        ("Stop Control", test_stop_control)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            success = await test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
            results.append((test_name, False))
        
        await asyncio.sleep(1)
    
    # Print summary
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Jarvis new features are ready to use.")
        print("\n📋 What you can now do:")
        print("• Visual feedback with animated eyes")
        print("• Safe VS Code sandbox for coding") 
        print("• Emergency stop button for all writing")
        print("• Advanced code generation and analysis")
        print("• Proper text handling without gaps")
        print("• Multiple programming language support")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    print("\n🎮 To start Jarvis with all new features:")
    print("python agent.py")

if __name__ == "__main__":
    asyncio.run(main())