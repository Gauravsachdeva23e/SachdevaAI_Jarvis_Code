"""
VS Code Sandbox Integration for Jarvis
Provides a safe coding environment with enhanced text handling and stop control
"""

import os
import subprocess
import tempfile
import json
import time
import logging
import asyncio
import threading
from pathlib import Path
from typing import Optional, Dict, List, Any
import pyautogui
import pygetwindow as gw
from langchain.tools import tool

from jarvis_visual import (
    get_visual_interface, should_stop_operation, 
    start_writing_session, stop_writing_session,
    add_activity_log, set_jarvis_state, JarvisState
)

logger = logging.getLogger(__name__)

class VSCodeSandbox:
    """VS Code sandbox environment for safe code writing"""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or self._create_sandbox_workspace()
        self.vscode_path = self._find_vscode_path()
        self.current_session = None
        self.is_writing = False
        self.write_thread = None
        self.char_delay = 0.02  # Delay between characters to fix gaps
        self.word_delay = 0.05  # Delay between words
        
        # Initialize workspace
        self._setup_workspace()
    
    def _find_vscode_path(self) -> str:
        """Find VS Code installation path"""
        possible_paths = [
            "C:\\Users\\{username}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
            "C:\\Program Files\\Microsoft VS Code\\Code.exe",
            "C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe"
        ]
        
        username = os.environ.get('USERNAME', 'User')
        for path in possible_paths:
            full_path = path.format(username=username)
            if os.path.exists(full_path):
                logger.info(f"Found VS Code at: {full_path}")
                return full_path
        
        # Fallback to system PATH
        return "code"
    
    def _create_sandbox_workspace(self) -> str:
        """Create a sandbox workspace directory"""
        sandbox_dir = Path.home() / "JarvisSandbox"
        sandbox_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (sandbox_dir / "projects").mkdir(exist_ok=True)
        (sandbox_dir / "temp").mkdir(exist_ok=True)
        (sandbox_dir / "scripts").mkdir(exist_ok=True)
        
        logger.info(f"Sandbox workspace created at: {sandbox_dir}")
        return str(sandbox_dir)
    
    def _setup_workspace(self):
        """Setup workspace with useful configurations"""
        # Create VS Code settings for better experience
        vscode_settings = {
            "editor.wordWrap": "on",
            "editor.minimap.enabled": False,
            "editor.fontSize": 14,
            "editor.fontFamily": "Consolas, 'Courier New', monospace",
            "editor.tabSize": 4,
            "editor.insertSpaces": True,
            "editor.autoSave": "afterDelay",
            "editor.autoSaveDelay": 1000,
            "workbench.colorTheme": "Dark+",
            "python.defaultInterpreterPath": "python",
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": True
        }
        settings_dir = Path(self.workspace_dir) / ".vscode"
        settings_dir.mkdir(exist_ok=True)
        
        with open(settings_dir / "settings.json", "w") as f:
            json.dump(vscode_settings, f, indent=4)
        
        # Create a README for the sandbox
        readme_content = """# Jarvis Sandbox Workspace

This is a safe coding environment created by Jarvis AI Assistant.

## Features:
- Safe isolated environment for code experiments
- Auto-save enabled
- Python linting and formatting
- Organized project structure

## Directories:
- `projects/` - Main project files
- `temp/` - Temporary files and experiments  
- `scripts/` - Utility scripts

## Usage:
- Use voice commands to create and edit files
- Say "stop writing" to halt any writing operation
- All changes are auto-saved

**Created by Jarvis AI Assistant**
"""
        
        with open(Path(self.workspace_dir) / "README.md", "w") as f:
            f.write(readme_content)
    
    def open_vscode(self, file_path: str = None) -> bool:
        """Open VS Code with the sandbox workspace"""
        try:
            cmd = [self.vscode_path, self.workspace_dir]
            if file_path:
                cmd.append(file_path)
            
            subprocess.Popen(cmd, shell=True)
            time.sleep(3)  # Wait for VS Code to load
            
            # Try to focus VS Code window
            self._focus_vscode_window()
            
            add_activity_log(f"VS Code opened with sandbox workspace: {self.workspace_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to open VS Code: {e}")
            add_activity_log(f"Error opening VS Code: {e}")
            return False
    
    def _focus_vscode_window(self) -> bool:
        """Focus on VS Code window"""
        try:
            windows = gw.getWindowsWithTitle("Visual Studio Code")
            if windows:
                window = windows[0]
                if window.isMinimized:
                    window.restore()
                window.activate()
                time.sleep(1)
                return True
        except Exception as e:
            logger.error(f"Could not focus VS Code window: {e}")
        return False
    
    def create_file(self, filename: str, content: str = "", file_type: str = "python") -> str:
        """Create a new file in the sandbox"""
        try:
            # Determine file extension
            extensions = {
                "python": ".py",
                "javascript": ".js", 
                "html": ".html",
                "css": ".css",
                "json": ".json",
                "markdown": ".md",
                "text": ".txt"
            }
            
            if not filename.endswith(tuple(extensions.values())):
                filename += extensions.get(file_type, ".txt")
            
            # Create in projects directory
            file_path = Path(self.workspace_dir) / "projects" / filename
            
            # Add template content based on file type
            if not content:
                content = self._get_template_content(file_type, filename)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            add_activity_log(f"Created file: {filename}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to create file {filename}: {e}")
            return ""
    
    def _get_template_content(self, file_type: str, filename: str) -> str:
        """Get template content for different file types"""
        templates = {
            "python": f'''"""
{filename}
Created by Jarvis AI Assistant
"""

def main():
    """Main function"""
    print("Hello from Jarvis!")

if __name__ == "__main__":
    main()
''',
            "javascript": f'''/**
 * {filename}
 * Created by Jarvis AI Assistant
 */

function main() {{
    console.log("Hello from Jarvis!");
}}

main();
''',
            "html": f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename}</title>
</head>
<body>
    <h1>Hello from Jarvis!</h1>
    <p>This file was created by Jarvis AI Assistant.</p>
</body>
</html>
''',
            "markdown": f'''# {filename}

Created by Jarvis AI Assistant

## Getting Started

This is a new markdown file ready for your content!
'''
        }
        
        return templates.get(file_type, f"# {filename}\n# Created by Jarvis AI Assistant\n\n")
    
    def safe_write_text(self, text: str, check_stop: bool = True) -> bool:
        """Safely write text with proper character handling and stop control"""
        if not text:
            return True
            
        try:
            # Focus VS Code first
            self._focus_vscode_window()
            time.sleep(0.5)
            
            # Split text into lines for better handling
            lines = text.split('\n')
            
            for line_idx, line in enumerate(lines):
                if check_stop and should_stop_operation():
                    add_activity_log("Writing stopped by user")
                    return False
                
                # Write line character by character to avoid gaps
                for char_idx, char in enumerate(line):
                    if check_stop and should_stop_operation():
                        return False
                    
                    # Handle special characters
                    if char == '\t':
                        pyautogui.press('tab')
                    elif char.isprintable():
                        # Use typewrite for better character handling
                        pyautogui.typewrite(char, interval=self.char_delay)
                    
                    # Small delay every few characters to prevent overwhelm
                    if char_idx > 0 and char_idx % 10 == 0:
                        time.sleep(self.word_delay)
                
                # Add newline if not last line
                if line_idx < len(lines) - 1:
                    pyautogui.press('enter')
                    time.sleep(self.char_delay * 2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error writing text: {e}")
            add_activity_log(f"Writing error: {e}")
            return False
    
    def write_code_with_formatting(self, code: str, language: str = "python") -> bool:
        """Write code with proper formatting and syntax highlighting"""
        try:
            start_writing_session(f"Writing {language} code...")
            
            # Add language-specific improvements
            if language == "python":
                code = self._improve_python_code(code)
            elif language == "javascript":
                code = self._improve_javascript_code(code)
            
            success = self.safe_write_text(code)
            
            if success:
                # Auto-format the code
                time.sleep(1)
                pyautogui.hotkey('shift', 'alt', 'f')  # Format document
                add_activity_log(f"Successfully wrote and formatted {language} code")
            
            stop_writing_session()
            return success
            
        except Exception as e:
            logger.error(f"Error writing {language} code: {e}")
            stop_writing_session()
            return False
    
    def _improve_python_code(self, code: str) -> str:
        """Improve Python code formatting and structure"""
        lines = code.split('\n')
        improved_lines = []
        
        for line in lines:
            line = line.rstrip()  # Remove trailing whitespace
            
            # Add proper spacing around operators
            line = line.replace('=', ' = ').replace('  =  ', ' = ')
            line = line.replace('+', ' + ').replace('  +  ', ' + ')
            line = line.replace('-', ' - ').replace('  -  ', ' - ')
            
            # Fix common issues
            line = line.replace('if(', 'if (')
            line = line.replace('for(', 'for (')
            line = line.replace('while(', 'while (')
            
            improved_lines.append(line)
        
        return '\n'.join(improved_lines)
    
    def _improve_javascript_code(self, code: str) -> str:
        """Improve JavaScript code formatting"""
        lines = code.split('\n')
        improved_lines = []
        
        for line in lines:
            line = line.rstrip()
            
            # Add semicolons if missing
            if line and not line.endswith((';', '{', '}', ')', ',')) and not line.startswith(('if', 'for', 'while', 'else')):
                line += ';'
            
            improved_lines.append(line)
        
        return '\n'.join(improved_lines)

# Global sandbox instance
_vscode_sandbox: Optional[VSCodeSandbox] = None

def get_sandbox() -> VSCodeSandbox:
    """Get or create VS Code sandbox instance"""
    global _vscode_sandbox
    if not _vscode_sandbox:
        _vscode_sandbox = VSCodeSandbox()
    return _vscode_sandbox

@tool
async def open_vscode_sandbox(project_name: str = "jarvis_project") -> str:
    """
    Open VS Code with a safe sandbox environment for coding.
    
    Use this when user wants to write code, create projects, or work in a safe environment.
    Example prompts:
    - "VS Code खोलो"
    - "Code लिखने के लिए editor खोलो"
    - "Programming environment चाहिए"
    """
    try:
        sandbox = get_sandbox()
        
        set_jarvis_state(JarvisState.THINKING, "Opening VS Code sandbox...")
        
        success = sandbox.open_vscode()
        if success:
            add_activity_log(f"VS Code sandbox opened for project: {project_name}")
            set_jarvis_state(JarvisState.IDLE, "VS Code ready for coding")
            return f"✅ VS Code sandbox opened successfully! Workspace: {sandbox.workspace_dir}"
        else:
            set_jarvis_state(JarvisState.ERROR, "Failed to open VS Code")
            return "❌ Failed to open VS Code. Please check if VS Code is installed."
            
    except Exception as e:
        logger.error(f"Error opening VS Code sandbox: {e}")
        return f"Error opening VS Code: {str(e)}"

@tool 
async def create_code_file(filename: str, file_type: str = "python", initial_content: str = "") -> str:
    """
    Create a new code file in the VS Code sandbox.
    
    Args:
        filename: Name of the file to create
        file_type: Type of file (python, javascript, html, css, etc.)
        initial_content: Optional initial content
    
    Example prompts:
    - "main.py बनाओ"
    - "New JavaScript file create करो"
    - "HTML page बनाना है"
    """
    try:
        sandbox = get_sandbox()
        file_path = sandbox.create_file(filename, initial_content, file_type)
        
        if file_path:
            # Open the created file in VS Code
            sandbox.open_vscode(file_path)
            add_activity_log(f"Created and opened {filename}")
            return f"✅ Created {filename} in sandbox. File opened in VS Code."
        else:
            return "❌ Failed to create file."
            
    except Exception as e:
        logger.error(f"Error creating file: {e}")
        return f"Error creating file: {str(e)}"

@tool
async def write_code(code_content: str, language: str = "python") -> str:
    """
    Write code in the currently active VS Code editor with proper formatting.
    
    Args:
        code_content: The code to write
        language: Programming language (python, javascript, html, etc.)
    
    Use this when user wants to write or dictate code.
    Example prompts:
    - "Python function लिखो"
    - "HTML structure create करो" 
    - "JavaScript code लिखना है"
    """
    try:
        sandbox = get_sandbox()
        
        # Ensure VS Code is focused
        sandbox._focus_vscode_window()
        
        success = sandbox.write_code_with_formatting(code_content, language)
        
        if success:
            return f"✅ Successfully wrote {language} code. Auto-formatted and ready!"
        else:
            return "❌ Writing was interrupted or failed."
            
    except Exception as e:
        logger.error(f"Error writing code: {e}")
        return f"Error writing code: {str(e)}"

@tool
async def safe_text_input(text: str) -> str:
    """
    Safely input text with proper character spacing and stop control.
    
    Use this for writing any text content with proper formatting.
    Example prompts:
    - "Comments लिखो"
    - "Documentation add करो"
    - "Text type करो"
    """
    try:
        sandbox = get_sandbox()
        
        start_writing_session("Writing text...")
        success = sandbox.safe_write_text(text)
        stop_writing_session()
        
        if success:
            return "✅ Text written successfully"
        else:
            return "❌ Text writing was stopped or failed"
            
    except Exception as e:
        logger.error(f"Error in safe text input: {e}")
        stop_writing_session()
        return f"Error writing text: {str(e)}"

@tool
async def stop_all_writing() -> str:
    """
    Emergency stop for all writing operations.
    
    Use this when user says "stop", "रुको", "बंद करो", etc.
    """
    try:
        visual = get_visual_interface()
        if visual:
            visual.emergency_stop()
        
        stop_writing_session()
        add_activity_log("🛑 All writing operations stopped by user command")
        
        return "🛑 All writing operations have been stopped."
        
    except Exception as e:
        return f"Error stopping operations: {str(e)}"