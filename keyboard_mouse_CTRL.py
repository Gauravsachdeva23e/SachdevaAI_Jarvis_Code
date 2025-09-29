import pyautogui
import asyncio
import time
from datetime import datetime
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from typing import List
from livekit.agents import function_tool
from langchain.tools import tool
import codecs

# ---------------------
# SafeController Class
# ---------------------
class SafeController:
    def __init__(self):
        self.active = False
        self.activation_time = None
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.valid_keys = set("abcdefghijklmnopqrstuvwxyz1234567890")
        self.special_keys = {
            "enter": Key.enter, "space": Key.space, "tab": Key.tab,
            "shift": Key.shift, "ctrl": Key.ctrl, "alt": Key.alt,
            "esc": Key.esc, "backspace": Key.backspace, "delete": Key.delete,
            "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
            "caps_lock": Key.caps_lock, "cmd": Key.cmd, "win": Key.cmd,
            "home": Key.home, "end": Key.end,
            "page_up": Key.page_up, "page_down": Key.page_down
        }

    def resolve_key(self, key):
        return self.special_keys.get(key.lower(), key)

    def log(self, action: str):
        with open("control_log.txt", "a") as f:
            f.write(f"{datetime.now()}: {action}\n")

    def activate(self, token=None):
        if token != "my_secret_token":
            self.log("Activation attempt failed.")
            return
        self.active = True
        self.activation_time = time.time()
        self.log("Controller auto-activated.")

    def deactivate(self):
        self.active = False
        self.log("Controller auto-deactivated.")

    def is_active(self):
        return self.active

    async def move_cursor(self, direction: str, distance: int = 100):
        if not self.is_active(): return "🛑 Controller is inactive."
        x, y = self.mouse.position
        if direction == "left": self.mouse.position = (x - distance, y)
        elif direction == "right": self.mouse.position = (x + distance, y)
        elif direction == "up": self.mouse.position = (x, y - distance)
        elif direction == "down": self.mouse.position = (x, y + distance)
        await asyncio.sleep(0.2)
        self.log(f"Mouse moved {direction}")
        return f"🖱️ Moved mouse {direction}."

    async def mouse_click(self, button: str = "left"):
        if not self.is_active(): return "🛑 Controller is inactive."
        if button == "left": self.mouse.click(Button.left, 1)
        elif button == "right": self.mouse.click(Button.right, 1)
        elif button == "double": self.mouse.click(Button.left, 2)
        await asyncio.sleep(0.2)
        self.log(f"Mouse clicked: {button}")
        return f"🖱️ {button.capitalize()} click."

    async def scroll_cursor(self, direction: str, amount: int = 10):
        if not self.is_active(): return "🛑 Controller is inactive."
        try:
            if direction == "up": self.mouse.scroll(0, amount)
            elif direction == "down": self.mouse.scroll(0, -amount)
        except:
            pyautogui.scroll(amount * 100)
        await asyncio.sleep(0.2)
        self.log(f"Mouse scrolled {direction}")
        return f"🖱️ Scrolled {direction}"

    async def type_text(self, text: str):
        if not self.is_active():
            return "🛑 Controller is inactive."

        # Fix: convert escaped sequences into real ones
        text = codecs.decode(text, "unicode_escape")

        for char in text:
            try:
                if char == "\n":
                    self.keyboard.press(Key.enter)
                    self.keyboard.release(Key.enter)
                elif char == "\t":
                    self.keyboard.press(Key.tab)
                    self.keyboard.release(Key.tab)
                elif char.isprintable():
                    self.keyboard.press(char)
                    self.keyboard.release(char)
                else:
                    continue

                await asyncio.sleep(0.05)

            except Exception:
                continue

        self.log(f"Typed text: {text}")
        return f"⌨️ Typed: {text}"

    async def press_key(self, key: str):
        if not self.is_active(): return "🛑 Controller is inactive."
        if key.lower() not in self.special_keys and key.lower() not in self.valid_keys:
            return f"❌ Invalid key: {key}"
        k = self.resolve_key(key)
        try:
            self.keyboard.press(k)
            self.keyboard.release(k)
        except Exception as e:
            return f"❌ Failed key: {key} — {e}"
        await asyncio.sleep(0.2)
        self.log(f"Pressed key: {key}")
        return f"⌨️ Key '{key}' pressed."

    async def press_hotkey(self, keys: List[str]):
        if not self.is_active(): return "🛑 Controller is inactive."
        resolved = []
        for k in keys:
            if k.lower() not in self.special_keys and k.lower() not in self.valid_keys:
                return f"❌ Invalid key in hotkey: {k}"
            resolved.append(self.resolve_key(k))

        for k in resolved: self.keyboard.press(k)
        for k in reversed(resolved): self.keyboard.release(k)
        await asyncio.sleep(0.3)
        self.log(f"Pressed hotkey: {' + '.join(keys)}")
        return f"⌨️ Hotkey {' + '.join(keys)} pressed."

    async def control_volume(self, action: str):
        if not self.is_active(): return "🛑 Controller is inactive."
        if action == "up": pyautogui.press("volumeup")
        elif action == "down": pyautogui.press("volumedown")
        elif action == "mute": pyautogui.press("volumemute")
        await asyncio.sleep(0.2)
        self.log(f"Volume control: {action}")
        return f"🔊 Volume {action}."

    async def swipe_gesture(self, direction: str):
        if not self.is_active(): return "🛑 Controller is inactive."
        screen_width, screen_height = pyautogui.size()
        x, y = screen_width // 2, screen_height // 2
        try:
            if direction == "up": pyautogui.moveTo(x, y + 200); pyautogui.dragTo(x, y - 200, duration=0.5)
            elif direction == "down": pyautogui.moveTo(x, y - 200); pyautogui.dragTo(x, y + 200, duration=0.5)
            elif direction == "left": pyautogui.moveTo(x + 200, y); pyautogui.dragTo(x - 200, y, duration=0.5)
            elif direction == "right": pyautogui.moveTo(x - 200, y); pyautogui.dragTo(x + 200, y, duration=0.5)
        except Exception:
            pass
        await asyncio.sleep(0.5)
        self.log(f"Swipe gesture: {direction}")
        return f"🖱️ Swipe {direction} done."

controller = SafeController()

async def with_temporary_activation(fn, *args, **kwargs):
    print(f"🔍 TEMP ACTIVATION: {fn.__name__} | args: {args}")
    controller.activate("my_secret_token")
    result = await fn(*args, **kwargs)
    await asyncio.sleep(2)
    controller.deactivate()
    return result

@tool
async def move_cursor_tool(direction: str, distance: int = 100):

    """
    Temporarily activates the controller and moves the mouse cursor in a specified direction.

    Args:
        direction (str): Direction to move the cursor. Must be one of ["up", "down", "left", "right"].
        distance (int, optional): Number of pixels to move the cursor. Defaults to 100.

    Returns:
        str: A message describing the mouse movement action.

    Note:
        The controller is automatically activated before the action and deactivated afterward.
    """


    return await with_temporary_activation(controller.move_cursor, direction, distance)

@tool
async def mouse_click_tool(button: str = "left"):

    """
    Temporarily activates the controller and performs a mouse click.

    Simulates clicking behavior for automation or voice command triggers.

    Args:
        button (str, optional): Type of mouse click to perform.
            Must be one of ["left", "right", "double"]. Defaults to "left".

    Returns:
        str: A message indicating the type of mouse click performed.

    Notes:
        - "double" simulates a double left-click.
        - Useful for GUI automation or hands-free system interaction.
    """


    return await with_temporary_activation(controller.mouse_click, button)

@tool
async def scroll_cursor_tool(direction: str, amount: int = 10):

    """
    Scrolls the screen vertically in the specified direction.

    Useful for commands like "scroll down" or "upar karo".

    Args:
        direction (str): The scroll direction. Must be either "up" or "down".
        amount (int, optional): The scroll intensity or number of scroll steps. Defaults to 10.

    Returns:
        str: A message indicating the direction and magnitude of the scroll action.

    Notes:
        - Positive `amount` values scroll further; can be tuned for smooth or fast scrolling.
        - Designed for fuzzy natural language control.
    """


    return await with_temporary_activation(controller.scroll_cursor, direction, amount)

@tool
async def type_text_tool(text: str):

    """
    Simulates typing the given text character by character, as if entered manually from a keyboard.

    Useful for commands like "type hello world" or "hello likho".

    Args:
        text (str): The full string to type, including spaces, punctuation, and symbols.

    Returns:
        str: A message confirming the typed input.
    """
    return await with_temporary_activation(controller.type_text, text)

@tool
async def press_key_tool(key: str):

    """
    Simulates pressing a single key on the keyboard, like Enter, Esc, or any letter/number.

    Useful for commands like "Enter दबाओ", "Escape दबाओ", or "A press करो".

    Args:
        key (str): The name of the key to press (e.g., "enter", "a", "ctrl", "esc").

    Returns:
        str: A message confirming the key press or an error if the key is invalid.
    """


    return await with_temporary_activation(controller.press_key, key)

@tool
async def press_hotkey_tool(keys: List[str]):

    """
    Simulates pressing a keyboard shortcut like Ctrl+S, Alt+F4, etc.

    Use this when the user says something like "save करो", "window बंद करो", 
    or "refresh कर दो".

    Args:
        keys (List[str]): List of key names to press together (e.g., ["ctrl", "s"]).

    Returns:
        str: A message indicating which hotkey combination was pressed.
    """


    return await with_temporary_activation(controller.press_hotkey, keys)

@tool
async def control_volume_tool(action: str):

    """
    Changes the system volume using keyboard emulation.

    Use this when the user says something like "volume बढ़ाओ", "mute कर दो", 
    or "lower the sound".

    Args:
        action (str): One of ["up", "down", "mute"].

    Returns:
        str: A message confirming the volume change.
    """


    return await with_temporary_activation(controller.control_volume, action)

@tool
async def swipe_gesture_tool(direction: str):

    """
    Simulates a swipe gesture on the screen using the mouse.

    Use this when the user wants to swipe in a direction like up, down, left, or right — 
    for example: "नीचे स्क्रॉल करो", "left swipe करो", or "screen ऊपर करो".

    Args:
        direction (str): One of ["up", "down", "left", "right"].

    Returns:
        str: A message describing the swipe action.
    """


    return await with_temporary_activation(controller.swipe_gesture, direction)

