"""
Intelligent Tool Orchestrator for Jarvis AI Assistant
Manages and intelligently selects tools based on user intent and context
"""

import re
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from jarvis_visual import set_jarvis_state, JarvisState, add_activity_log

logger = logging.getLogger(__name__)

class ToolCategory(Enum):
    """Categories of tools for better organization"""
    SYSTEM_INFO = "system_info"
    FILE_MANAGEMENT = "file_management" 
    CODE_DEVELOPMENT = "code_development"
    WEB_SEARCH = "web_search"
    COMMUNICATION = "communication"
    AUTOMATION = "automation"
    MULTIMEDIA = "multimedia"
    PRODUCTIVITY = "productivity"
    LEARNING = "learning"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"

@dataclass
class ToolMetadata:
    """Metadata for each tool"""
    name: str
    category: ToolCategory
    description: str
    keywords: List[str]
    priority: int  # Higher number = higher priority
    prerequisites: List[str] = None  # Required tools or conditions
    conflicts: List[str] = None  # Conflicting tools
    min_confidence: float = 0.7  # Minimum confidence to use this tool
    async_capable: bool = True
    estimated_time: float = 1.0  # Estimated execution time in seconds

class IntentClassifier:
    """Classifies user intent to determine appropriate tools"""
    
    def __init__(self):
        self.intent_patterns = {
            # System and Information
            "system_info": [
                r"system.*info|hardware|specs|performance|cpu|memory|ram|disk",
                r"computer.*details|pc.*info|machine.*specs",
                r"how much.*ram|storage.*space|processor.*speed"
            ],
            
            # File and Folder Operations
            "file_operations": [
                r"file|folder|directory|create.*file|open.*file|delete.*file",
                r"बनाओ|खोलो|delete करो|फ़ाइल|फोल्डर",
                r"make.*folder|new.*directory|copy.*file"
            ],
            
            # Code Development
            "code_development": [
                r"code|program|script|function|class|app|website|api",
                r"python|javascript|html|css|react|flask|fastapi|node",
                r"vs code|वीएस कोड|कोड लिखो|प्रोग्राम बनाओ",
                r"bug|debug|error|fix.*code|analyze.*code"
            ],
            
            # Search and Information
            "web_search": [
                r"search|google|find.*information|look.*up|research",
                r"खोजो|ढूंढो|information|जानकारी|search करो",
                r"what.*is|how.*to|tell.*me.*about"
            ],
            
            # Weather and Location
            "weather": [
                r"weather|temperature|rain|climate|मौसम|बारिश|तापमान",
                r"forecast|humidity|wind|clouds|sunny|cloudy"
            ],
            
            # Automation and Control
            "automation": [
                r"automate|control|keyboard|mouse|click|type|press",
                r"volume|cursor|scroll|hotkey|shortcut",
                r"automation|macro|script.*run"
            ],
            
            # Writing and Text
            "writing": [
                r"write|type|text|document|note|letter|email",
                r"लिखो|टाइप करो|text.*input|compose",
                r"draft|content|article|blog|story"
            ],
            
            # Multimedia
            "multimedia": [
                r"play.*music|video|audio|image|photo|picture",
                r"media|song|movie|gallery|camera|screenshot",
                r"record|capture|stream"
            ],
            
            # Learning and Education  
            "learning": [
                r"learn|study|tutorial|course|lesson|teach|explain",
                r"education|knowledge|skill|training|practice",
                r"सिखाओ|समझाओ|tutorial|guide"
            ],
            
            # Entertainment
            "entertainment": [
                r"game|fun|joke|story|quiz|puzzle|music|movie",
                r"entertainment|leisure|hobby|recreation",
                r"मजा|खेल|कहानी|गाना"
            ],
            
            # Productivity
            "productivity": [
                r"schedule|calendar|reminder|todo|task|meeting|appointment",
                r"organize|plan|manage|productivity|efficiency",
                r"काम|कार्य|meeting|reminder"
            ],
            
            # Communication
            "communication": [
                r"email|message|send|call|chat|contact|whatsapp|telegram",
                r"communicate|reply|respond|forward|share",
                r"संदेश|मैसेज|भेजो|call करो"
            ]
        }
        
        # Hinglish keyword mappings
        self.hinglish_mappings = {
            "खोलो": "open",
            "बंद करो": "close", 
            "बनाओ": "create",
            "लिखो": "write",
            "भेजो": "send",
            "ढूंढो": "search",
            "चलाओ": "play",
            "रुको": "stop",
            "सिस्टम": "system",
            "फ़ाइल": "file",
            "फोल्डर": "folder",
            "कोड": "code",
            "प्रोग्राम": "program"
        }
    
    def classify_intent(self, query: str) -> Dict[str, float]:
        """Classify user intent with confidence scores"""
        query_lower = query.lower()
        
        # Normalize Hinglish terms
        for hindi, english in self.hinglish_mappings.items():
            query_lower = query_lower.replace(hindi, english)
        
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            max_score = 0.0
            
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    # Calculate confidence based on pattern match strength
                    matches = len(re.findall(pattern, query_lower))
                    pattern_strength = min(matches * 0.3, 1.0)
                    max_score = max(max_score, pattern_strength)
            
            if max_score > 0:
                intent_scores[intent] = max_score
        
        # Boost scores for exact keyword matches
        for intent, score in intent_scores.items():
            if intent in query_lower:
                intent_scores[intent] = min(score + 0.2, 1.0)
        
        return dict(sorted(intent_scores.items(), key=lambda x: x[1], reverse=True))

class ToolOrchestrator:
    """Main orchestrator that manages and selects tools intelligently"""
    
    def __init__(self):
        self.classifier = IntentClassifier()
        self.tool_registry = {}
        self.tool_usage_history = []
        self.context_memory = {}
        self.active_session = None
        
        # Initialize tool registry
        self._initialize_tool_registry()
    
    def _initialize_tool_registry(self):
        """Initialize the tool registry with metadata"""
        self.tool_registry = {
            # System Information Tools
            "get_system_info": ToolMetadata(
                "get_system_info", ToolCategory.SYSTEM_INFO,
                "Get comprehensive system information including CPU, memory, disk usage",
                ["system", "info", "hardware", "specs", "performance", "cpu", "memory", "ram"],
                priority=8, estimated_time=2.0
            ),
            "get_running_processes": ToolMetadata(
                "get_running_processes", ToolCategory.SYSTEM_INFO,
                "Get list of running processes and resource usage",
                ["processes", "running", "tasks", "cpu", "memory", "performance"],
                priority=7, estimated_time=3.0
            ),
            "get_network_info": ToolMetadata(
                "get_network_info", ToolCategory.SYSTEM_INFO,
                "Get network information and connectivity status",
                ["network", "ip", "internet", "connection", "wifi"],
                priority=6, estimated_time=2.0
            ),
            "cleanup_system": ToolMetadata(
                "cleanup_system", ToolCategory.UTILITIES,
                "Clean temporary files and optimize system performance",
                ["clean", "cleanup", "optimize", "temp", "space", "storage"],
                priority=5, estimated_time=10.0
            ),
            
            # File Management Tools
            "open_app": ToolMetadata(
                "open_app", ToolCategory.FILE_MANAGEMENT,
                "Open desktop applications",
                ["open", "launch", "start", "app", "application", "program"],
                priority=9, estimated_time=3.0
            ),
            "close_app": ToolMetadata(
                "close_app", ToolCategory.FILE_MANAGEMENT,
                "Close running applications",
                ["close", "quit", "exit", "stop", "end", "terminate"],
                priority=8, estimated_time=1.0
            ),
            "folder_file": ToolMetadata(
                "folder_file", ToolCategory.FILE_MANAGEMENT,
                "Handle folder and file operations like create, rename, delete",
                ["folder", "file", "create", "delete", "rename", "manage"],
                priority=8, estimated_time=2.0
            ),
            "Play_file": ToolMetadata(
                "Play_file", ToolCategory.MULTIMEDIA,
                "Open and play files like videos, documents, images",
                ["play", "open", "file", "video", "music", "document", "image"],
                priority=7, estimated_time=2.0
            ),
            
            # Code Development Tools
            "open_vscode_sandbox": ToolMetadata(
                "open_vscode_sandbox", ToolCategory.CODE_DEVELOPMENT,
                "Open VS Code with safe sandbox environment for coding",
                ["vscode", "code", "editor", "ide", "programming", "development"],
                priority=9, estimated_time=5.0
            ),
            "create_code_file": ToolMetadata(
                "create_code_file", ToolCategory.CODE_DEVELOPMENT,
                "Create new code files with templates",
                ["create", "file", "code", "python", "javascript", "html", "new"],
                priority=8, estimated_time=2.0,
                prerequisites=["open_vscode_sandbox"]
            ),
            "write_code": ToolMetadata(
                "write_code", ToolCategory.CODE_DEVELOPMENT,
                "Write code with proper formatting and syntax highlighting",
                ["write", "code", "type", "program", "script", "function"],
                priority=8, estimated_time=10.0,
                prerequisites=["open_vscode_sandbox"]
            ),
            "analyze_code": ToolMetadata(
                "analyze_code", ToolCategory.CODE_DEVELOPMENT,
                "Analyze code for errors, style issues, and improvements",
                ["analyze", "check", "review", "debug", "error", "bug"],
                priority=7, estimated_time=3.0
            ),
            "generate_function": ToolMetadata(
                "generate_function", ToolCategory.CODE_DEVELOPMENT,
                "Generate function templates with documentation",
                ["function", "generate", "template", "create", "method"],
                priority=7, estimated_time=3.0
            ),
            "generate_class": ToolMetadata(
                "generate_class", ToolCategory.CODE_DEVELOPMENT,
                "Generate class templates with methods",
                ["class", "generate", "template", "create", "object"],
                priority=7, estimated_time=4.0
            ),
            "create_web_app": ToolMetadata(
                "create_web_app", ToolCategory.CODE_DEVELOPMENT,
                "Generate complete web application templates",
                ["web", "app", "website", "api", "server", "flask", "fastapi", "express"],
                priority=6, estimated_time=8.0
            ),
            
            # Search and Information Tools
            "google_search": ToolMetadata(
                "google_search", ToolCategory.WEB_SEARCH,
                "Search Google for information with speech-friendly results",
                ["search", "google", "find", "information", "research", "lookup"],
                priority=9, estimated_time=3.0
            ),
            "get_weather": ToolMetadata(
                "get_weather", ToolCategory.WEB_SEARCH,
                "Get current weather information for any city",
                ["weather", "temperature", "rain", "climate", "forecast"],
                priority=8, estimated_time=2.0
            ),
            "get_current_datetime": ToolMetadata(
                "get_current_datetime", ToolCategory.UTILITIES,
                "Get current date and time",
                ["time", "date", "clock", "current", "now"],
                priority=9, estimated_time=0.1
            ),
            
            # Automation Tools
            "move_cursor_tool": ToolMetadata(
                "move_cursor_tool", ToolCategory.AUTOMATION,
                "Move mouse cursor in specified direction",
                ["cursor", "mouse", "move", "pointer"],
                priority=6, estimated_time=0.5
            ),
            "mouse_click_tool": ToolMetadata(
                "mouse_click_tool", ToolCategory.AUTOMATION,
                "Perform mouse clicks (left, right, double)",
                ["click", "mouse", "press", "select"],
                priority=7, estimated_time=0.5
            ),
            "type_text_tool": ToolMetadata(
                "type_text_tool", ToolCategory.AUTOMATION,
                "Type text safely with proper character handling",
                ["type", "text", "write", "input", "keyboard"],
                priority=8, estimated_time=5.0
            ),
            "press_key_tool": ToolMetadata(
                "press_key_tool", ToolCategory.AUTOMATION,
                "Press individual keyboard keys",
                ["key", "press", "keyboard", "button"],
                priority=7, estimated_time=0.5
            ),
            "control_volume_tool": ToolMetadata(
                "control_volume_tool", ToolCategory.AUTOMATION,
                "Control system volume (up, down, mute)",
                ["volume", "sound", "audio", "mute", "speaker"],
                priority=6, estimated_time=0.5
            ),
            
            # Text and Writing Tools
            "safe_text_input": ToolMetadata(
                "safe_text_input", ToolCategory.PRODUCTIVITY,
                "Safely input text with proper formatting and stop control",
                ["text", "write", "input", "type", "safe"],
                priority=8, estimated_time=8.0
            ),
            "stop_all_writing": ToolMetadata(
                "stop_all_writing", ToolCategory.UTILITIES,
                "Emergency stop for all writing operations",
                ["stop", "halt", "cancel", "emergency", "abort"],
                priority=10, estimated_time=0.1
            )
        }
    
    def register_tool(self, tool_name: str, metadata: ToolMetadata):
        """Register a new tool with the orchestrator"""
        self.tool_registry[tool_name] = metadata
        logger.info(f"Registered tool: {tool_name}")
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query and determine appropriate tools"""
        set_jarvis_state(JarvisState.THINKING, "Analyzing your request...")
        
        # Classify intent
        intents = self.classifier.classify_intent(query)
        
        # Find matching tools
        matching_tools = []
        
        for tool_name, metadata in self.tool_registry.items():
            tool_score = 0.0
            
            # Check if any tool keywords match the query
            query_lower = query.lower()
            for keyword in metadata.keywords:
                if keyword in query_lower:
                    tool_score += 0.3
            
            # Boost score based on intent classification
            category_name = metadata.category.value
            if category_name in intents:
                tool_score += intents[category_name] * 0.7
            
            # Apply priority weighting
            tool_score *= (metadata.priority / 10.0)
            
            if tool_score >= metadata.min_confidence:
                matching_tools.append((tool_name, metadata, tool_score))
        
        # Sort by score
        matching_tools.sort(key=lambda x: x[2], reverse=True)
        
        analysis = {
            "query": query,
            "intents": intents,
            "matching_tools": matching_tools[:5],  # Top 5 tools
            "primary_intent": list(intents.keys())[0] if intents else "general",
            "confidence": list(intents.values())[0] if intents else 0.5
        }
        
        add_activity_log(f"Found {len(matching_tools)} matching tools for: {query[:50]}...")
        return analysis
    
    def select_tools(self, analysis: Dict[str, Any]) -> List[Tuple[str, ToolMetadata]]:
        """Select the best tools for execution"""
        selected_tools = []
        used_categories = set()
        
        for tool_name, metadata, score in analysis["matching_tools"]:
            # Avoid tool conflicts
            if metadata.conflicts:
                if any(conflict in [t[0] for t in selected_tools] for conflict in metadata.conflicts):
                    continue
            
            # Limit tools per category (except utilities)
            if metadata.category != ToolCategory.UTILITIES:
                if metadata.category in used_categories:
                    continue
                used_categories.add(metadata.category)
            
            selected_tools.append((tool_name, metadata))
            
            # Limit total tools for performance
            if len(selected_tools) >= 3:
                break
        
        return selected_tools
    
    def create_execution_plan(self, selected_tools: List[Tuple[str, ToolMetadata]], query: str) -> Dict[str, Any]:
        """Create an execution plan for the selected tools"""
        plan = {
            "tools": [],
            "estimated_time": 0,
            "requires_prerequisites": False,
            "has_conflicts": False,
            "execution_order": []
        }
        
        # Sort tools by dependencies and priority
        sorted_tools = []
        prerequisite_tools = []
        
        for tool_name, metadata in selected_tools:
            if metadata.prerequisites:
                # Check if prerequisites are met
                for prereq in metadata.prerequisites:
                    if prereq not in [t[0] for t in selected_tools]:
                        prerequisite_tools.append(prereq)
                        plan["requires_prerequisites"] = True
            
            sorted_tools.append((tool_name, metadata))
            plan["estimated_time"] += metadata.estimated_time
        
        # Add prerequisite tools if needed
        for prereq in prerequisite_tools:
            if prereq in self.tool_registry:
                prereq_metadata = self.tool_registry[prereq]
                sorted_tools.insert(0, (prereq, prereq_metadata))
                plan["estimated_time"] += prereq_metadata.estimated_time
        
        plan["tools"] = sorted_tools
        plan["execution_order"] = [tool[0] for tool in sorted_tools]
        
        return plan
    
    async def execute_plan(self, plan: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Execute the planned tools"""
        set_jarvis_state(JarvisState.THINKING, f"Executing {len(plan['tools'])} tools...")
        
        results = {
            "success": True,
            "tool_results": {},
            "execution_time": 0,
            "errors": []
        }
        
        start_time = asyncio.get_event_loop().time()
        
        for tool_name, metadata in plan["tools"]:
            try:
                add_activity_log(f"Executing: {tool_name}")
                set_jarvis_state(JarvisState.THINKING, f"Running {metadata.name}...")
                
                # Import and execute tool dynamically
                tool_result = await self._execute_tool(tool_name, query)
                results["tool_results"][tool_name] = tool_result
                
                # Log usage for learning
                self.tool_usage_history.append({
                    "tool": tool_name,
                    "query": query,
                    "success": True,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
            except Exception as e:
                error_msg = f"Error executing {tool_name}: {str(e)}"
                results["errors"].append(error_msg)
                results["success"] = False
                logger.error(error_msg)
                
                add_activity_log(f"❌ {tool_name} failed: {str(e)[:50]}")
        
        results["execution_time"] = asyncio.get_event_loop().time() - start_time
        
        if results["success"]:
            set_jarvis_state(JarvisState.IDLE, "Task completed successfully")
            add_activity_log(f"✅ Completed in {results['execution_time']:.1f}s")
        else:
            set_jarvis_state(JarvisState.ERROR, "Some tools failed to execute")
        
        return results
    
    async def _execute_tool(self, tool_name: str, query: str) -> Any:
        """Dynamically execute a tool"""
        # Import the appropriate module and execute the tool
        try:
            if tool_name.startswith("get_system"):
                from system_utilities import get_system_info, get_running_processes, get_network_info, cleanup_system
                if tool_name == "get_system_info":
                    return await get_system_info()
                elif tool_name == "get_running_processes":
                    return await get_running_processes()
                elif tool_name == "get_network_info":
                    return await get_network_info()
            
            elif "vscode" in tool_name or "code" in tool_name:
                from vscode_sandbox import open_vscode_sandbox, create_code_file, write_code, safe_text_input
                from coding_tools import analyze_code, generate_function, generate_class, create_web_app
                
                if tool_name == "open_vscode_sandbox":
                    return await open_vscode_sandbox()
                elif tool_name == "write_code":
                    return await write_code(query)
                elif tool_name == "analyze_code":
                    return await analyze_code(query)
                elif tool_name == "generate_function":
                    return await generate_function("user_function", query)
                elif tool_name == "create_web_app":
                    return await create_web_app("user_app")
            
            elif tool_name in ["google_search", "get_weather", "get_current_datetime"]:
                from Jarvis_google_search import google_search, get_current_datetime
                from jarvis_get_whether import get_weather
                
                if tool_name == "google_search":
                    return await google_search(query)
                elif tool_name == "get_weather":
                    return await get_weather()
                elif tool_name == "get_current_datetime":
                    return await get_current_datetime()
            
            elif tool_name in ["open_app", "close_app", "folder_file", "Play_file"]:
                from Jarvis_window_CTRL import open_app, close_app, folder_file
                from Jarvis_file_opner import Play_file
                
                if tool_name == "open_app":
                    return await open_app(query)
                elif tool_name == "close_app":
                    return await close_app(query)
                elif tool_name == "folder_file":
                    return await folder_file(query)
                elif tool_name == "Play_file":
                    return await Play_file(query)
            
            elif "tool" in tool_name:  # Automation tools
                from keyboard_mouse_CTRL import (
                    move_cursor_tool, mouse_click_tool, type_text_tool,
                    press_key_tool, control_volume_tool
                )
                
                if tool_name == "type_text_tool":
                    return await type_text_tool(query)
                elif tool_name == "mouse_click_tool":
                    return await mouse_click_tool()
                elif tool_name == "control_volume_tool":
                    return await control_volume_tool("up")  # Default action
            
            else:
                return f"Tool {tool_name} executed with query: {query}"
                
        except Exception as e:
            raise Exception(f"Failed to execute {tool_name}: {str(e)}")
    
    async def process_query(self, query: str) -> str:
        """Main method to process a user query"""
        try:
            # Step 1: Analyze the query
            analysis = self.analyze_query(query)
            
            if not analysis["matching_tools"]:
                return "I'm not sure how to help with that. Could you be more specific?"
            
            # Step 2: Select appropriate tools
            selected_tools = self.select_tools(analysis)
            
            if not selected_tools:
                return "I couldn't find appropriate tools for your request."
            
            # Step 3: Create execution plan
            plan = self.create_execution_plan(selected_tools, query)
            
            # Step 4: Execute the plan
            results = await self.execute_plan(plan, query)
            
            # Step 5: Format and return results
            if results["success"]:
                tool_outputs = []
                for tool_name, result in results["tool_results"].items():
                    if isinstance(result, str) and result:
                        tool_outputs.append(result)
                
                if tool_outputs:
                    return "\\n\\n".join(tool_outputs)
                else:
                    return "Task completed successfully!"
            else:
                error_summary = "\\n".join(results["errors"][:3])  # Show first 3 errors
                return f"Some operations failed:\\n{error_summary}"
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            set_jarvis_state(JarvisState.ERROR, "Processing failed")
            return f"I encountered an error while processing your request: {str(e)}"

# Global orchestrator instance
_orchestrator = None

def get_orchestrator() -> ToolOrchestrator:
    """Get or create the global orchestrator instance"""
    global _orchestrator
    if not _orchestrator:
        _orchestrator = ToolOrchestrator()
    return _orchestrator

async def smart_tool_execution(query: str) -> str:
    """Smart tool execution using the orchestrator"""
    orchestrator = get_orchestrator()
    return await orchestrator.process_query(query)