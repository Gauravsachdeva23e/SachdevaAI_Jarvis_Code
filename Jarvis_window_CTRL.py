import os
import subprocess
import logging
import sys
import asyncio
from fuzzywuzzy import process

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

from langchain.tools import tool

# Setup encoding and logger
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App command map with dynamic path detection
def get_app_mappings():
    """Get app mappings with dynamic path detection"""
    base_mappings = {
        "notepad": "notepad",
        "calculator": "calc",
        "command prompt": "cmd",
        "cmd": "cmd",
        "control panel": "control",
        "settings": "start ms-settings:",
        "paint": "mspaint",
        "file explorer": "explorer",
        "task manager": "taskmgr",
        "registry editor": "regedit",
        "device manager": "devmgmt.msc"
    }
    
    # Try to detect common applications dynamically
    common_paths = {
        "chrome": [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ],
        "firefox": [
            "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
        ],
        "vlc": [
            "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
            "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe"
        ],
        "vs code": [
            f"C:\\Users\\{os.environ.get('USERNAME', 'User')}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
            "C:\\Program Files\\Microsoft VS Code\\Code.exe"
        ],
        "postman": [
            f"C:\\Users\\{os.environ.get('USERNAME', 'User')}\\AppData\\Local\\Postman\\Postman.exe"
        ]
    }
    
    # Add existing paths that exist on the system
    for app, paths in common_paths.items():
        for path in paths:
            if os.path.exists(path):
                base_mappings[app] = path
                break
        else:
            # If no path found, just use the app name and let Windows find it
            base_mappings[app] = app
    
    return base_mappings

APP_MAPPINGS = get_app_mappings()

# -------------------------
# Global focus utility
# -------------------------
async def focus_window(title_keyword: str) -> bool:
    if not gw:
        logger.warning("⚠ pygetwindow")
        return False

    await asyncio.sleep(1.5)  # Give time for window to appear
    title_keyword = title_keyword.lower().strip()

    for window in gw.getAllWindows():
        if title_keyword in window.title.lower():
            if window.isMinimized:
                window.restore()
            window.activate()
            return True
    return False

# Index files/folders with caching and performance optimization
_index_cache = {}
_cache_timestamp = {}
CACHE_DURATION = 300  # 5 minutes

async def index_items(base_dirs, max_depth=3, max_items=1000):
    """Index files and folders with caching and limits for performance"""
    import time
    
    cache_key = str(sorted(base_dirs))
    current_time = time.time()
    
    # Check cache first
    if (cache_key in _index_cache and 
        cache_key in _cache_timestamp and 
        current_time - _cache_timestamp[cache_key] < CACHE_DURATION):
        logger.info(f"Using cached index with {len(_index_cache[cache_key])} items")
        return _index_cache[cache_key]
    
    item_index = []
    items_processed = 0
    
    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            logger.warning(f"Directory does not exist: {base_dir}")
            continue
            
        try:
            for root, dirs, files in os.walk(base_dir):
                # Limit search depth for performance
                level = root.replace(base_dir, '').count(os.sep)
                if level >= max_depth:
                    dirs[:] = []  # Don't recurse deeper
                    continue
                
                # Add folders
                for d in dirs[:50]:  # Limit to first 50 dirs per level
                    if items_processed >= max_items:
                        break
                    item_index.append({
                        "name": d, 
                        "path": os.path.join(root, d), 
                        "type": "folder",
                        "size": 0
                    })
                    items_processed += 1
                
                # Add files
                for f in files[:100]:  # Limit to first 100 files per directory
                    if items_processed >= max_items:
                        break
                    try:
                        file_path = os.path.join(root, f)
                        file_size = os.path.getsize(file_path)
                        item_index.append({
                            "name": f, 
                            "path": file_path, 
                            "type": "file",
                            "size": file_size
                        })
                        items_processed += 1
                    except (OSError, PermissionError):
                        continue  # Skip files we can't access
                
                if items_processed >= max_items:
                    logger.warning(f"Reached maximum items limit ({max_items}), stopping indexing")
                    break
                    
        except (PermissionError, OSError) as e:
            logger.warning(f"Cannot access directory {base_dir}: {e}")
            continue
    
    # Cache the results
    _index_cache[cache_key] = item_index
    _cache_timestamp[cache_key] = current_time
    
    logger.info(f"✅ Indexed {len(item_index)} items from {len(base_dirs)} directories")
    return item_index

async def search_item(query, index, item_type):
    filtered = [item for item in index if item["type"] == item_type]
    choices = [item["name"] for item in filtered]
    if not choices:
        return None
    best_match, score = process.extractOne(query, choices)
    logger.info(f"🔍 Matched '{query}' to '{best_match}' with score {score}")
    if score > 70:
        for item in filtered:
            if item["name"] == best_match:
                return item
    return None

# File/folder actions
async def open_folder(path):
    try:
        os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
        await focus_window(os.path.basename(path))
    except Exception as e:
        logger.error(f"❌ फ़ाइल open करने में error आया। {e}")

async def play_file(path):
    try:
        os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
        await focus_window(os.path.basename(path))
    except Exception as e:
        logger.error(f"❌ फ़ाइल open करने में error आया।: {e}")

async def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"✅ Folder create हो गया।: {path}"
    except Exception as e:
        return f"❌ फ़ाइल create करने में error आया।: {e}"

async def rename_item(old_path, new_path):
    try:
        os.rename(old_path, new_path)
        return f"✅ नाम बदलकर {new_path} कर दिया गया।"
    except Exception as e:
        return f"❌ नाम बदलना fail हो गया: {e}"

async def delete_item(path):
    try:
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
        return f"🗑️ Deleted: {path}"
    except Exception as e:
        return f"❌ Delete नहीं हुआ।: {e}"

# App control
@tool
async def open_app(app_title: str) -> str:

    """
    open_app a desktop app like Notepad, Chrome, VLC, etc.

    Use this tool when the user asks to launch an application on their computer.
    Example prompts:
    - "Notepad खोलो"
    - "Chrome open करो"
    - "VLC media player चलाओ"
    - "Calculator launch करो"
    """


    app_title = app_title.lower().strip()
    app_command = APP_MAPPINGS.get(app_title, app_title)
    try:
        await asyncio.create_subprocess_shell(f'start "" "{app_command}"', shell=True)
        focused = await focus_window(app_title)
        if focused:
            return f"🚀 App launch हुआ और focus में है: {app_title}."
        else:
            return f"🚀 {app_title} Launch किया गया, लेकिन window पर focus नहीं हो पाया।"
    except Exception as e:
        return f"❌ {app_title} Launch नहीं हो पाया।: {e}"

@tool
async def close_app(window_title: str) -> str:

    """
    Closes the applications window by its title.

    Use this tool when the user wants to close any app or window on their desktop.
    Example prompts:
    - "Notepad बंद करो"
    - "Close VLC"
    - "Chrome की window बंद कर दो"
    - "Calculator को बंद करो"
    """


    if not win32gui:
        return "❌ win32gui"

    def enumHandler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if window_title.lower() in win32gui.GetWindowText(hwnd).lower():
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    win32gui.EnumWindows(enumHandler, None)
    return f"❌ Window बंद हो गई है।: {window_title}"

# Jarvis command logic
@tool
async def folder_file(command: str) -> str:

    """
    Handles folder and file actions like open, create, rename, or delete based on user command.

    Use this tool when the user wants to manage folders or files using natural language.
    Example prompts:
    - "Projects folder बनाओ"
    - "OldName को NewName में rename करो"
    - "xyz.mp4 delete कर दो"
    - "Music folder खोलो"
    - "Resume.pdf चलाओ"
    """


    folders_to_index = ["D:/"]
    index = await index_items(folders_to_index)
    command_lower = command.lower()

    if "create folder" in command_lower:
        folder_name = command.replace("create folder", "").strip()
        path = os.path.join("D:/", folder_name)
        return await create_folder(path)

    if "rename" in command_lower:
        parts = command_lower.replace("rename", "").strip().split("to")
        if len(parts) == 2:
            old_name = parts[0].strip()
            new_name = parts[1].strip()
            item = await search_item(old_name, index, "folder")
            if item:
                new_path = os.path.join(os.path.dirname(item["path"]), new_name)
                return await rename_item(item["path"], new_path)
        return "❌ rename command valid नहीं है।"

    if "delete" in command_lower:
        item = await search_item(command, index, "folder") or await search_item(command, index, "file")
        if item:
            return await delete_item(item["path"])
        return "❌ Delete करने के लिए item नहीं मिला।"

    if "folder" in command_lower or "open folder" in command_lower:
        item = await search_item(command, index, "folder")
        if item:
            await open_folder(item["path"])
            return f"✅ Folder opened: {item['name']}"
        return "❌ Folder नहीं मिला।."

    item = await search_item(command, index, "file")
    if item:
        await play_file(item["path"])
        return f"✅ File opened: {item['name']}"

    return "⚠ कुछ भी match नहीं हुआ।"
