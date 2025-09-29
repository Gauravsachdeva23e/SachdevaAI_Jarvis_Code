"""
Jarvis Visual Interface - Eyes and Status Display
Provides visual feedback and status indication for Jarvis operations
"""

import tkinter as tk
from tkinter import ttk, Canvas
import math
import threading
import time
import logging
from typing import Optional, Dict, Any
import asyncio
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class JarvisState(Enum):
    IDLE = "idle"
    LISTENING = "listening" 
    THINKING = "thinking"
    SPEAKING = "speaking"
    WRITING = "writing"
    ERROR = "error"
    SLEEPING = "sleeping"

@dataclass
class EyeConfig:
    """Configuration for Jarvis eyes"""
    pupil_size: int = 15
    iris_size: int = 35
    eye_size: int = 60
    blink_duration: float = 0.15
    look_speed: float = 2.0

class JarvisEyes:
    """Animated eyes for Jarvis with emotion and state indication"""
    
    def __init__(self, master):
        self.master = master
        self.config = EyeConfig()
        self.current_state = JarvisState.IDLE
        self.is_running = True
        self.is_writing = False
        self.stop_writing = threading.Event()
        
        # Eye position and animation variables
        self.pupil_x = 0
        self.pupil_y = 0
        self.target_x = 0
        self.target_y = 0
        self.blink_timer = 0
        self.is_blinking = False
        
        # Color schemes for different states
        self.state_colors = {
            JarvisState.IDLE: {"bg": "#000011", "iris": "#4A90E2", "pupil": "#000000", "glow": "#6BB6FF"},
            JarvisState.LISTENING: {"bg": "#001100", "iris": "#50C878", "pupil": "#000000", "glow": "#7FFF00"},
            JarvisState.THINKING: {"bg": "#110011", "iris": "#9966CC", "pupil": "#000000", "glow": "#DA70D6"},
            JarvisState.SPEAKING: {"bg": "#110000", "iris": "#FF6B6B", "pupil": "#000000", "glow": "#FF8C8C"},
            JarvisState.WRITING: {"bg": "#111100", "iris": "#FFD700", "pupil": "#000000", "glow": "#FFFF66"},
            JarvisState.ERROR: {"bg": "#220000", "iris": "#FF4444", "pupil": "#000000", "glow": "#FF6666"},
            JarvisState.SLEEPING: {"bg": "#000000", "iris": "#333333", "pupil": "#111111", "glow": "#444444"}
        }
        
        self.setup_ui()
        self.start_animation_thread()
    
    def setup_ui(self):
        """Setup the visual interface"""
        self.master.title("Jarvis - AI Assistant")
        self.master.configure(bg='#000011')
        self.master.geometry("400x300")
        self.master.attributes('-topmost', True)
        self.master.attributes('-alpha', 0.9)
        
        # Main frame
        self.main_frame = tk.Frame(self.master, bg='#000011')
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Eyes canvas
        self.canvas = Canvas(
            self.main_frame,
            width=300,
            height=150,
            bg='#000011',
            highlightthickness=0
        )
        self.canvas.pack(pady=10)
        
        # Status display
        self.status_label = tk.Label(
            self.main_frame,
            text="JARVIS - Ready",
            font=('Arial', 14, 'bold'),
            fg='#4A90E2',
            bg='#000011'
        )
        self.status_label.pack(pady=5)
        
        # Activity indicator
        self.activity_text = tk.Text(
            self.main_frame,
            height=6,
            width=50,
            bg='#001122',
            fg='#CCCCCC',
            font=('Consolas', 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.activity_text.pack(pady=5, fill='both', expand=True)
        
        # Control buttons
        self.button_frame = tk.Frame(self.main_frame, bg='#000011')
        self.button_frame.pack(pady=5)
        
        self.stop_button = tk.Button(
            self.button_frame,
            text="🛑 STOP WRITING",
            command=self.emergency_stop,
            bg='#FF4444',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='raised',
            bd=3
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.minimize_button = tk.Button(
            self.button_frame,
            text="➖ Minimize",
            command=self.master.iconify,
            bg='#4A90E2',
            fg='white',
            font=('Arial', 9),
            relief='raised'
        )
        self.minimize_button.pack(side=tk.LEFT, padx=5)
        
        self.dashboard_button = tk.Button(
            self.button_frame,
            text="🛠️ Tools",
            command=self.open_dashboard,
            bg='#9966CC',
            fg='white',
            font=('Arial', 9),
            relief='raised'
        )
        self.dashboard_button.pack(side=tk.LEFT, padx=5)
        
        # Close button handler
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def draw_eyes(self):
        """Draw the animated eyes"""
        self.canvas.delete("all")
        
        colors = self.state_colors[self.current_state]
        
        # Eye positions
        left_eye_x, left_eye_y = 80, 75
        right_eye_x, right_eye_y = 220, 75
        
        for eye_x, eye_y in [(left_eye_x, left_eye_y), (right_eye_x, right_eye_y)]:
            # Draw eye background with glow effect
            glow_size = self.config.eye_size + 10
            self.canvas.create_oval(
                eye_x - glow_size//2, eye_y - glow_size//2,
                eye_x + glow_size//2, eye_y + glow_size//2,
                fill=colors["glow"], outline="", stipple="gray50"
            )
            
            # Draw eye white
            eye_radius = self.config.eye_size // 2
            self.canvas.create_oval(
                eye_x - eye_radius, eye_y - eye_radius,
                eye_x + eye_radius, eye_y + eye_radius,
                fill='white', outline=colors["iris"], width=2
            )
            
            if not self.is_blinking:
                # Draw iris
                iris_x = eye_x + self.pupil_x * 0.6
                iris_y = eye_y + self.pupil_y * 0.6
                iris_radius = self.config.iris_size // 2
                
                self.canvas.create_oval(
                    iris_x - iris_radius, iris_y - iris_radius,
                    iris_x + iris_radius, iris_y + iris_radius,
                    fill=colors["iris"], outline=colors["glow"], width=1
                )
                
                # Draw pupil
                pupil_radius = self.config.pupil_size // 2
                self.canvas.create_oval(
                    iris_x - pupil_radius, iris_y - pupil_radius,
                    iris_x + pupil_radius, iris_y + pupil_radius,
                    fill=colors["pupil"], outline=""
                )
                
                # Add sparkle for liveliness
                sparkle_x = iris_x - pupil_radius // 3
                sparkle_y = iris_y - pupil_radius // 3
                self.canvas.create_oval(
                    sparkle_x - 2, sparkle_y - 2,
                    sparkle_x + 2, sparkle_y + 2,
                    fill='white', outline=""
                )
            else:
                # Draw closed eye (blink)
                self.canvas.create_line(
                    eye_x - eye_radius, eye_y,
                    eye_x + eye_radius, eye_y,
                    fill=colors["iris"], width=3
                )
    
    def update_animation(self):
        """Update eye animation"""
        # Smooth pupil movement
        diff_x = self.target_x - self.pupil_x
        diff_y = self.target_y - self.pupil_y
        
        self.pupil_x += diff_x * 0.1
        self.pupil_y += diff_y * 0.1
        
        # Random eye movement when idle
        if self.current_state == JarvisState.IDLE and abs(diff_x) < 2 and abs(diff_y) < 2:
            if time.time() % 3 < 0.1:  # Change direction occasionally
                self.target_x = (time.time() % 4 - 2) * 10
                self.target_y = (time.time() % 3 - 1.5) * 8
        
        # Blinking logic
        self.blink_timer += 0.05
        if self.blink_timer > 3 + (time.time() % 4):  # Random blink intervals
            self.is_blinking = True
            if self.blink_timer > 3.2 + (time.time() % 4):
                self.is_blinking = False
                self.blink_timer = 0
        
        # Special animations based on state
        if self.current_state == JarvisState.WRITING:
            # Typing animation - eyes follow text
            self.target_x = math.sin(time.time() * 3) * 15
            self.target_y = -5
        elif self.current_state == JarvisState.THINKING:
            # Thinking animation - eyes move in circles
            angle = time.time() * 2
            self.target_x = math.cos(angle) * 12
            self.target_y = math.sin(angle) * 8
        elif self.current_state == JarvisState.LISTENING:
            # Alert and focused
            self.target_x = 0
            self.target_y = -2
    
    def set_state(self, state: JarvisState, message: str = ""):
        """Change Jarvis state and update visuals"""
        self.current_state = state
        
        # Update status label
        status_text = f"JARVIS - {state.value.upper()}"
        if message:
            status_text += f": {message}"
        
        self.status_label.config(
            text=status_text,
            fg=self.state_colors[state]["iris"]
        )
        
        # Add message to activity log
        if message:
            self.add_activity_message(f"[{state.value.upper()}] {message}")
        
        logger.info(f"Jarvis state changed to: {state.value} - {message}")
    
    def add_activity_message(self, message: str):
        """Add message to activity log"""
        self.activity_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.activity_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.activity_text.see(tk.END)
        self.activity_text.config(state=tk.DISABLED)
    
    def emergency_stop(self):
        """Emergency stop for all operations"""
        self.stop_writing.set()
        self.is_writing = False
        self.set_state(JarvisState.IDLE, "Operation stopped by user")
        self.add_activity_message("🛑 EMERGENCY STOP - All operations halted")
        
        # Try to stop any ongoing writing operations
        try:
            import pyautogui
            pyautogui.hotkey('ctrl', 'z')  # Undo last action
        except:
            pass
    
    def start_writing_mode(self, task_description: str = "Writing..."):
        """Start writing mode with visual feedback"""
        self.is_writing = True
        self.stop_writing.clear()
        self.set_state(JarvisState.WRITING, task_description)
        self.stop_button.config(bg='#FF2222', text='🛑 STOP NOW!')
    
    def stop_writing_mode(self):
        """Stop writing mode"""
        self.is_writing = False
        self.stop_writing.set()
        self.set_state(JarvisState.IDLE, "Writing stopped")
        self.stop_button.config(bg='#FF4444', text='🛑 STOP WRITING')
    
    def should_stop_writing(self) -> bool:
        """Check if writing should be stopped"""
        return self.stop_writing.is_set()
    
    def start_animation_thread(self):
        """Start the animation thread"""
        def animation_loop():
            while self.is_running:
                try:
                    self.update_animation()
                    self.draw_eyes()
                    time.sleep(0.05)  # 20 FPS
                except Exception as e:
                    logger.error(f"Animation error: {e}")
                    time.sleep(0.1)
        
        self.animation_thread = threading.Thread(target=animation_loop, daemon=True)
        self.animation_thread.start()
    
    def open_dashboard(self):
        """Open tool management dashboard"""
        try:
            # Import and launch dashboard in separate thread
            def launch_dashboard():
                from tool_dashboard import ToolDashboard
                dashboard = ToolDashboard()
                dashboard.run()
            
            import threading
            dashboard_thread = threading.Thread(target=launch_dashboard, daemon=True)
            dashboard_thread.start()
            
            self.add_activity_message("🛠️ Tool management dashboard opened")
        except Exception as e:
            self.add_activity_message(f"❌ Error opening dashboard: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        self.is_running = False
        self.emergency_stop()
        self.master.quit()
        self.master.destroy()

# Global instance for easy access
_jarvis_visual: Optional[JarvisEyes] = None

def initialize_visual_interface():
    """Initialize the Jarvis visual interface"""
    global _jarvis_visual
    
    def setup_ui():
        root = tk.Tk()
        _jarvis_visual = JarvisEyes(root)
        root.mainloop()
    
    # Run in separate thread
    ui_thread = threading.Thread(target=setup_ui, daemon=True)
    ui_thread.start()
    
    # Wait a moment for initialization
    time.sleep(1)
    return _jarvis_visual

def get_visual_interface() -> Optional[JarvisEyes]:
    """Get the current visual interface instance"""
    return _jarvis_visual

def set_jarvis_state(state: JarvisState, message: str = ""):
    """Set Jarvis state (convenience function)"""
    if _jarvis_visual:
        _jarvis_visual.set_state(state, message)

def start_writing_session(description: str = "Writing code..."):
    """Start a writing session with visual feedback"""
    if _jarvis_visual:
        _jarvis_visual.start_writing_mode(description)

def stop_writing_session():
    """Stop current writing session"""
    if _jarvis_visual:
        _jarvis_visual.stop_writing_mode()

def should_stop_operation() -> bool:
    """Check if operations should be stopped"""
    return _jarvis_visual.should_stop_writing() if _jarvis_visual else False

def add_activity_log(message: str):
    """Add message to activity log"""
    if _jarvis_visual:
        _jarvis_visual.add_activity_message(message)

if __name__ == "__main__":
    # Test the visual interface
    visual = initialize_visual_interface()
    
    # Demo state changes
    import time
    time.sleep(2)
    set_jarvis_state(JarvisState.LISTENING, "Listening for commands...")
    time.sleep(3)
    set_jarvis_state(JarvisState.THINKING, "Processing request...")
    time.sleep(2)
    start_writing_session("Writing Python code...")
    time.sleep(5)
    stop_writing_session()
    
    input("Press Enter to exit...")