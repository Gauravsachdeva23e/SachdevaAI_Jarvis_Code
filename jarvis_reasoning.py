"""Jarvis Reasoning Module - Advanced AI Agent with Tool Orchestration

This module provides an intelligent reasoning system that combines LangChain agents
with custom tool orchestration for comprehensive AI assistant capabilities.

Features:
- Intelligent tool selection and execution
- Multi-language support (English/Hindi)
- Comprehensive error handling and logging
- Performance monitoring and caching
- Fallback strategies for robust operation
"""

import asyncio
import logging
import time
from functools import lru_cache
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from contextlib import asynccontextmanager

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from dotenv import load_dotenv
from livekit.agents import function_tool

# Tool imports - organized by category
from Jarvis_google_search import google_search, get_current_datetime
from jarvis_get_whether import get_weather
from Jarvis_window_CTRL import open_app, close_app, folder_file
from Jarvis_file_opner import Play_file
from keyboard_mouse_CTRL import (
    move_cursor_tool, mouse_click_tool, scroll_cursor_tool, 
    type_text_tool, press_key_tool, swipe_gesture_tool, 
    press_hotkey_tool, control_volume_tool)
from system_utilities import (
    get_system_info, get_running_processes, get_network_info,
    cleanup_system, get_installed_programs)
from vscode_sandbox import (
    open_vscode_sandbox, create_code_file, write_code,
    safe_text_input, stop_all_writing)
from coding_tools import (
    analyze_code, fix_code, generate_function, generate_class,
    create_web_app, create_data_analysis_script)
from advanced_tools import (
    create_task, show_tasks, complete_task_by_name,
    explain_concept, create_study_plan,
    tell_joke, random_fact,
    calculate_expression, unit_converter, generate_password)
from tool_orchestrator import smart_tool_execution

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('jarvis_reasoning.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class JarvisConfig:
    """Configuration settings for Jarvis reasoning system"""
    model_name: str = "gemini-2.0-flash"
    max_retries: int = 3
    timeout_seconds: float = 30.0
    orchestrator_threshold: int = 10
    verbose_mode: bool = True
    cache_size: int = 128
    min_query_length: int = 1
    max_query_length: int = 1000
    enable_fallback: bool = True
    log_performance: bool = True


@dataclass
class PerformanceMetrics:
    """Performance tracking for reasoning operations"""
    total_queries: int = 0
    successful_queries: int = 0
    orchestrator_queries: int = 0
    langchain_queries: int = 0
    average_response_time: float = 0.0
    total_response_time: float = 0.0
    error_count: int = 0
    last_error: Optional[str] = None
    
    def update_success(self, response_time: float, method: str) -> None:
        """Update metrics for successful query"""
        self.total_queries += 1
        self.successful_queries += 1
        self.total_response_time += response_time
        self.average_response_time = self.total_response_time / self.total_queries
        
        if method == "orchestrator":
            self.orchestrator_queries += 1
        else:
            self.langchain_queries += 1
    
    def update_error(self, error_msg: str) -> None:
        """Update metrics for failed query"""
        self.total_queries += 1
        self.error_count += 1
        self.last_error = error_msg
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_queries == 0:
            return 0.0
        return (self.successful_queries / self.total_queries) * 100


class JarvisError(Exception):
    """Custom exception for Jarvis reasoning errors"""
    def __init__(self, message: str, error_code: str = "UNKNOWN", original_error: Exception = None):
        super().__init__(message)
        self.error_code = error_code
        self.original_error = original_error
        self.timestamp = time.time()


# Global configuration and metrics
_config = JarvisConfig()
_metrics = PerformanceMetrics()
_cached_agent = None
_cached_tools = None
_last_cache_time = 0
CACHE_TIMEOUT = 300  # 5 minutes


def validate_query(query: str) -> None:
    """Validate input query parameters
    
    Args:
        query: The user query string to validate
        
    Raises:
        JarvisError: If query is invalid
    """
    if not query or not isinstance(query, str):
        raise JarvisError("Query must be a non-empty string", "INVALID_QUERY")
    
    query = query.strip()
    if len(query) < _config.min_query_length:
        raise JarvisError(f"Query too short (minimum {_config.min_query_length} characters)", "QUERY_TOO_SHORT")
    
    if len(query) > _config.max_query_length:
        raise JarvisError(f"Query too long (maximum {_config.max_query_length} characters)", "QUERY_TOO_LONG")


@lru_cache(maxsize=128)
def get_tool_list() -> List[Any]:
    """Get cached list of available tools
    
    Returns:
        List of tool functions for the agent
    """
    return [
        # Search and Information
        google_search,
        get_current_datetime,
        get_weather,
        
        # System Control
        open_app,
        close_app,
        folder_file,
        Play_file,
        
        # Input Control
        move_cursor_tool,
        mouse_click_tool,
        scroll_cursor_tool,
        type_text_tool,
        press_key_tool,
        press_hotkey_tool,
        control_volume_tool,
        swipe_gesture_tool,
        
        # System Utilities
        get_system_info,
        get_running_processes,
        get_network_info,
        cleanup_system,
        get_installed_programs,
        
        # VS Code Sandbox
        open_vscode_sandbox,
        create_code_file,
        write_code,
        safe_text_input,
        stop_all_writing,
        
        # Coding Tools
        analyze_code,
        fix_code,
        generate_function,
        generate_class,
        create_web_app,
        create_data_analysis_script,
        
        # Productivity Tools
        create_task,
        show_tasks,
        complete_task_by_name,
        
        # Learning Tools
        explain_concept,
        create_study_plan,
        
        # Entertainment Tools
        tell_joke,
        random_fact,
        
        # Utility Tools
        calculate_expression,
        unit_converter,
        generate_password
    ]


def get_cached_agent() -> Optional[AgentExecutor]:
    """Get cached agent if available and not expired
    
    Returns:
        Cached AgentExecutor or None if cache expired
    """
    global _cached_agent, _last_cache_time
    
    current_time = time.time()
    if _cached_agent and (current_time - _last_cache_time) < CACHE_TIMEOUT:
        logger.debug("Using cached agent")
        return _cached_agent
    
    return None


def cache_agent(agent: AgentExecutor) -> None:
    """Cache the agent for future use
    
    Args:
        agent: The AgentExecutor to cache
    """
    global _cached_agent, _last_cache_time
    _cached_agent = agent
    _last_cache_time = time.time()
    logger.debug("Agent cached successfully")


async def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0) -> Any:
    """Retry function with exponential backoff
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        
    Returns:
        Result of the function call
        
    Raises:
        JarvisError: If all retries are exhausted
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")
    
    raise JarvisError(
        f"Operation failed after {max_retries + 1} attempts",
        "RETRY_EXHAUSTED",
        last_exception
    )


@asynccontextmanager
async def performance_monitor(operation_name: str):
    """Context manager for performance monitoring
    
    Args:
        operation_name: Name of the operation being monitored
    """
    start_time = time.time()
    logger.debug(f"Starting operation: {operation_name}")
    
    try:
        yield
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Operation '{operation_name}' completed in {duration:.2f}s")
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        logger.error(f"Operation '{operation_name}' failed after {duration:.2f}s: {e}")
        raise

@function_tool(
    name="thinking_capability",
    description=(
        "Advanced AI reasoning and tool orchestration system with comprehensive capabilities:\n"
        "• Intelligent tool selection with confidence scoring\n"
        "• Multi-language support (English/Hindi/Hinglish)\n"
        "• Code development, analysis, and debugging\n"
        "• File and system management operations\n"
        "• Web search and real-time information retrieval\n"
        "• Productivity and task management tools\n"
        "• Learning and educational resources\n"
        "• Entertainment and utility functions\n"
        "• Automation and control systems\n"
        "• Performance monitoring and error recovery\n"
        "Uses advanced intent classification and caching for optimal performance."
))
async def thinking_capability(query: str) -> Dict[str, Any]:
    """Advanced AI reasoning and tool execution system.
    
    This function serves as the main entry point for Jarvis's reasoning capabilities.
    It intelligently analyzes user queries, selects appropriate tools, and executes
    them with comprehensive error handling and performance monitoring.
    
    Args:
        query (str): Natural language query from the user. Can be in English, Hindi,
                    or Hinglish. Must be between 1-1000 characters.
    
    Returns:
        Dict[str, Any]: Response dictionary containing:
            - success (bool): Whether the operation was successful
            - response (str): The actual response content
            - method (str): Execution method used ("orchestrator" or "langchain")
            - execution_time (float): Time taken to process the query
            - error_code (str, optional): Error code if operation failed
            - error (str, optional): Error message if operation failed
    
    Raises:
        JarvisError: For validation errors or configuration issues
        
    Examples:
        >>> await thinking_capability("What's the weather like?")
        {'success': True, 'response': 'Current weather...', 'method': 'orchestrator'}
        
        >>> await thinking_capability("कोड लिखो")
        {'success': True, 'response': 'Opening VS Code...', 'method': 'orchestrator'}
    """
    start_time = time.time()
    
    try:
        # Input validation
        validate_query(query)
        query = query.strip()
        
        # Log query start
        logger.info(f"Processing query: '{query[:100]}{'...' if len(query) > 100 else ''}'")
        
        # Try orchestrator first (fast path)
        async with performance_monitor("orchestrator_execution"):
            orchestrator_result = await _try_orchestrator(query)
            if orchestrator_result:
                execution_time = time.time() - start_time
                _metrics.update_success(execution_time, "orchestrator")
                
                return {
                    "success": True,
                    "response": orchestrator_result,
                    "method": "orchestrator",
                    "execution_time": execution_time
                }
        
        # Fallback to LangChain agent (comprehensive path)
        if _config.enable_fallback:
            async with performance_monitor("langchain_execution"):
                langchain_result = await _try_langchain_agent(query)
                execution_time = time.time() - start_time
                _metrics.update_success(execution_time, "langchain")
                
                return {
                    "success": True,
                    "response": langchain_result,
                    "method": "langchain",
                    "execution_time": execution_time
                }
        
        # If both methods fail or are disabled
        raise JarvisError("No available execution method could handle the query", "NO_METHOD_AVAILABLE")
    
    except JarvisError as je:
        execution_time = time.time() - start_time
        _metrics.update_error(f"{je.error_code}: {str(je)}")
        logger.error(f"Jarvis error: {je.error_code} - {je}")
        
        return {
            "success": False,
            "error": str(je),
            "error_code": je.error_code,
            "execution_time": execution_time
        }
    
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Unexpected error in thinking_capability: {str(e)}"
        _metrics.update_error(error_msg)
        logger.error(error_msg, exc_info=True)
        
        return {
            "success": False,
            "error": "An unexpected error occurred while processing your request",
            "error_code": "UNEXPECTED_ERROR",
            "execution_time": execution_time
        }


async def _try_orchestrator(query: str) -> Optional[str]:
    """Try to execute query using the intelligent orchestrator.
    
    Args:
        query: The user query to process
        
    Returns:
        String response if successful, None if failed or inadequate response
        
    Raises:
        JarvisError: If orchestrator execution fails critically
    """
    try:
        orchestrator_result = await retry_with_backoff(
            lambda: smart_tool_execution(query),
            max_retries=_config.max_retries
        )
        
        # Check if orchestrator provided a meaningful response
        if orchestrator_result and len(orchestrator_result.strip()) > _config.orchestrator_threshold:
            logger.info("Orchestrator successfully handled the query")
            return orchestrator_result.strip()
        
        logger.debug("Orchestrator response insufficient, trying fallback")
        return None
        
    except Exception as e:
        logger.warning(f"Orchestrator execution failed: {e}")
        if not _config.enable_fallback:
            raise JarvisError(f"Orchestrator failed and fallback disabled: {e}", "ORCHESTRATOR_FAILED")
        return None


async def _try_langchain_agent(query: str) -> str:
    """Execute query using LangChain agent as fallback.
    
    Args:
        query: The user query to process
        
    Returns:
        String response from the agent
        
    Raises:
        JarvisError: If agent creation or execution fails
    """
    try:
        # Try to use cached agent first
        executor = get_cached_agent()
        
        if not executor:
            logger.info("Creating new LangChain agent")
            executor = await _create_langchain_agent()
            cache_agent(executor)
        
        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                executor.ainvoke({"input": query}),
                timeout=_config.timeout_seconds
            )
        except asyncio.TimeoutError:
            raise JarvisError(f"Query execution timed out after {_config.timeout_seconds}s", "EXECUTION_TIMEOUT")
        
        # Extract response from result
        if isinstance(result, dict) and 'output' in result:
            response = result['output']
        else:
            response = str(result)
        
        if not response or not response.strip():
            raise JarvisError("LangChain agent returned empty response", "EMPTY_RESPONSE")
        
        logger.info("LangChain agent successfully processed the query")
        return response.strip()
        
    except JarvisError:
        raise  # Re-raise Jarvis errors
    except Exception as e:
        raise JarvisError(f"LangChain agent execution failed: {e}", "LANGCHAIN_FAILED", e)


async def _create_langchain_agent() -> AgentExecutor:
    """Create a new LangChain agent with current configuration.
    
    Returns:
        Configured AgentExecutor instance
        
    Raises:
        JarvisError: If agent creation fails
    """
    try:
        # Initialize model
        model = ChatGoogleGenerativeAI(
            model=_config.model_name,
            temperature=0.1,  # Lower temperature for more consistent responses
            max_tokens=2048
        )
        
        # Get prompt template
        prompt = hub.pull("hwchase17/react")
        
        # Get tools list
        tools = get_tool_list()
        
        # Create agent
        agent = create_react_agent(
            llm=model,
            tools=tools,
            prompt=prompt
        )
        
        # Create executor
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=_config.verbose_mode,
            max_iterations=10,
            max_execution_time=_config.timeout_seconds,
            handle_parsing_errors=True
        )
        
        logger.info(f"Created LangChain agent with {len(tools)} tools")
        return executor
        
    except Exception as e:
        raise JarvisError(f"Failed to create LangChain agent: {e}", "AGENT_CREATION_FAILED", e)


# Additional utility functions for external access
def get_performance_metrics() -> Dict[str, Any]:
    """Get current performance metrics.
    
    Returns:
        Dictionary containing current performance statistics
    """
    return {
        "total_queries": _metrics.total_queries,
        "success_rate": _metrics.get_success_rate(),
        "average_response_time": _metrics.average_response_time,
        "orchestrator_usage": _metrics.orchestrator_queries,
        "langchain_usage": _metrics.langchain_queries,
        "error_count": _metrics.error_count,
        "last_error": _metrics.last_error
    }


def reset_performance_metrics() -> None:
    """Reset performance metrics to initial state."""
    global _metrics
    _metrics = PerformanceMetrics()
    logger.info("Performance metrics reset")


def update_configuration(**kwargs) -> None:
    """Update configuration parameters.
    
    Args:
        **kwargs: Configuration parameters to update
    """
    global _config
    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)
            logger.info(f"Configuration updated: {key} = {value}")
        else:
            logger.warning(f"Unknown configuration parameter: {key}")
