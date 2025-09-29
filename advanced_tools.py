"""
Advanced Tools Collection for Jarvis AI Assistant
Contains specialized tools for productivity, communication, learning, and entertainment
"""

import os
import subprocess
import json
import logging
import asyncio
import time
import requests
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import calendar
import random
from pathlib import Path
from langchain.tools import tool

from jarvis_visual import add_activity_log, set_jarvis_state, JarvisState
from vscode_sandbox import get_sandbox

logger = logging.getLogger(__name__)

# ====================
# PRODUCTIVITY TOOLS
# ====================

class TaskManager:
    """Simple task and reminder management"""
    
    def __init__(self):
        self.db_path = Path.home() / "JarvisSandbox" / "tasks.db"
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the tasks database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                due_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT,
                remind_at TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_task(self, title: str, description: str = "", priority: str = "medium", due_date: str = "") -> bool:
        """Add a new task"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks (title, description, priority, due_date)
                VALUES (?, ?, ?, ?)
            ''', (title, description, priority, due_date))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            return False
    
    def get_tasks(self, status: str = "all") -> List[Dict]:
        """Get tasks by status"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            if status == "all":
                cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            else:
                cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC", (status,))
            
            columns = [desc[0] for desc in cursor.description]
            tasks = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return tasks
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            return []
    
    def complete_task(self, task_id: int) -> bool:
        """Mark task as completed"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tasks 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (task_id,))
            
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return False

# Global task manager instance
_task_manager = TaskManager()

@tool
async def create_task(title: str, description: str = "", priority: str = "medium") -> str:
    """
    Create a new task or todo item.
    
    Args:
        title: Task title/name
        description: Detailed description of the task
        priority: Task priority (low, medium, high)
    
    Example prompts:
    - "Task बनाओ - Complete project report"
    - "Reminder add करो - Call dentist tomorrow"
    - "Todo में add करो - Buy groceries"
    """
    try:
        success = _task_manager.add_task(title, description, priority)
        if success:
            add_activity_log(f"Task created: {title}")
            return f"✅ Task created successfully: '{title}' with priority {priority}"
        else:
            return "❌ Failed to create task"
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return f"Error creating task: {str(e)}"

@tool
async def show_tasks(status: str = "pending") -> str:
    """
    Show your tasks and todo items.
    
    Args:
        status: Task status to filter by (pending, completed, all)
    
    Example prompts:
    - "मेरे tasks दिखाओ"
    - "Pending work बताओ"
    - "Todo list show करो"
    """
    try:
        tasks = _task_manager.get_tasks(status)
        
        if not tasks:
            return f"No {status} tasks found."
        
        result = [f"📋 Your {status} tasks ({len(tasks)} items):"]
        result.append("=" * 40)
        
        for i, task in enumerate(tasks[:10], 1):  # Show max 10 tasks
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task['priority'], "⚪")
            status_emoji = {"completed": "✅", "pending": "⏳", "in_progress": "🔄"}.get(task['status'], "❓")
            
            result.append(f"{i:2d}. {status_emoji} {priority_emoji} {task['title']}")
            if task['description']:
                result.append(f"     📝 {task['description'][:60]}...")
            if task['due_date']:
                result.append(f"     📅 Due: {task['due_date']}")
            result.append("")
        
        add_activity_log(f"Showed {len(tasks)} {status} tasks")
        return "\n".join(result)
        
    except Exception as e:
        logger.error(f"Error showing tasks: {e}")
        return f"Error retrieving tasks: {str(e)}"

@tool
async def complete_task_by_name(task_title: str) -> str:
    """
    Mark a task as completed by its title.
    
    Args:
        task_title: Title of the task to complete
    
    Example prompts:
    - "Complete project report task को complete करो"
    - "Mark done - Buy groceries"
    - "Finish करो - Call dentist"
    """
    try:
        tasks = _task_manager.get_tasks("pending")
        
        # Find matching task
        matching_task = None
        for task in tasks:
            if task_title.lower() in task['title'].lower():
                matching_task = task
                break
        
        if not matching_task:
            return f"❌ Task '{task_title}' not found in pending tasks"
        
        success = _task_manager.complete_task(matching_task['id'])
        if success:
            add_activity_log(f"Task completed: {matching_task['title']}")
            return f"✅ Task completed: '{matching_task['title']}'"
        else:
            return f"❌ Failed to complete task"
            
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return f"Error completing task: {str(e)}"

# ====================
# LEARNING TOOLS
# ====================

@tool
async def explain_concept(concept: str, level: str = "beginner") -> str:
    """
    Explain a concept or technology in simple terms.
    
    Args:
        concept: The concept to explain
        level: Explanation level (beginner, intermediate, advanced)
    
    Example prompts:
    - "Machine learning क्या है?"
    - "Blockchain समझाओ"
    - "Python decorators explain करो"
    """
    try:
        set_jarvis_state(JarvisState.THINKING, f"Explaining {concept}...")
        
        # Create a simple explanation based on common concepts
        explanations = {
            "machine learning": {
                "beginner": "Machine Learning is like teaching a computer to learn patterns from data, just like how humans learn from experience. Instead of programming every rule, we show the computer examples and it learns to make predictions.",
                "intermediate": "Machine Learning involves algorithms that can identify patterns in data and make predictions or decisions without being explicitly programmed for each specific task. It includes supervised, unsupervised, and reinforcement learning.",
                "advanced": "Machine Learning encompasses statistical and computational techniques that enable systems to automatically improve performance through experience, utilizing mathematical optimization, probability theory, and algorithmic complexity."
            },
            "blockchain": {
                "beginner": "Blockchain is like a digital ledger that keeps records of transactions. Instead of one person controlling it, many computers work together to verify and store the information securely.",
                "intermediate": "Blockchain is a distributed ledger technology that maintains a continuously growing list of records (blocks) that are cryptographically linked and resistant to modification.",
                "advanced": "Blockchain implements a decentralized consensus mechanism using cryptographic hash functions, merkle trees, and proof-of-work/stake algorithms to achieve Byzantine fault tolerance."
            },
            "artificial intelligence": {
                "beginner": "AI is computer technology that tries to make machines think and act like humans. It can recognize speech, understand images, and solve problems.",
                "intermediate": "Artificial Intelligence involves creating computer systems that can perform tasks typically requiring human intelligence, including learning, reasoning, perception, and decision-making.",
                "advanced": "AI encompasses computational systems that exhibit cognitive functions including machine learning, natural language processing, computer vision, robotics, and expert systems."
            }
        }
        
        concept_lower = concept.lower()
        explanation = None
        
        # Find matching explanation
        for key, levels in explanations.items():
            if key in concept_lower or concept_lower in key:
                explanation = levels.get(level, levels.get("beginner"))
                break
        
        if not explanation:
            # Generate a generic explanation
            explanation = f"I'd be happy to explain {concept}! This is a complex topic that involves various aspects and applications. To provide the best explanation, could you specify what particular aspect you'd like to understand?"
        
        # Create educational content
        result = [
            f"📚 EXPLANATION: {concept.title()}",
            "=" * 50,
            f"Level: {level.title()}",
            "",
            explanation,
            "",
            "💡 Tips for learning more:",
            "• Break down complex topics into smaller parts",
            "• Look for practical examples and applications", 
            "• Practice with hands-on projects",
            "• Connect new concepts to what you already know"
        ]
        
        add_activity_log(f"Explained concept: {concept}")
        return "\n".join(result)
        
    except Exception as e:
        logger.error(f"Error explaining concept: {e}")
        return f"Error explaining {concept}: {str(e)}"

@tool
async def create_study_plan(topic: str, duration_days: int = 7) -> str:
    """
    Create a structured study plan for learning a topic.
    
    Args:
        topic: Subject or skill to learn
        duration_days: Number of days for the study plan
    
    Example prompts:
    - "Python सीखने के लिए study plan बनाओ"
    - "Web development का 2 week plan चाहिए"
    - "Data science study schedule create करो"
    """
    try:
        set_jarvis_state(JarvisState.THINKING, f"Creating study plan for {topic}...")
        
        # Study plan templates
        study_plans = {
            "python": [
                "Day 1-2: Python basics - Variables, data types, operators",
                "Day 3-4: Control structures - If statements, loops", 
                "Day 5-6: Functions and modules",
                "Day 7-8: Object-oriented programming",
                "Day 9-10: File handling and error handling",
                "Day 11-12: Libraries (requests, json, datetime)",
                "Day 13-14: Practice projects and review"
            ],
            "web development": [
                "Day 1-2: HTML fundamentals and structure",
                "Day 3-4: CSS styling and layouts",
                "Day 5-6: JavaScript basics and DOM manipulation",
                "Day 7-8: Responsive design and frameworks",
                "Day 9-10: Backend concepts (Node.js or Python)",
                "Day 11-12: Databases and APIs",
                "Day 13-14: Full project development"
            ],
            "data science": [
                "Day 1-2: Statistics and mathematics review",
                "Day 3-4: Python for data science (pandas, numpy)",
                "Day 5-6: Data visualization (matplotlib, seaborn)",
                "Day 7-8: Machine learning basics",
                "Day 9-10: Data preprocessing and cleaning",
                "Day 11-12: Model building and evaluation", 
                "Day 13-14: Practice project and presentation"
            ]
        }
        
        # Find matching study plan
        plan_items = []
        topic_lower = topic.lower()
        
        for key, items in study_plans.items():
            if key in topic_lower or topic_lower in key:
                plan_items = items
                break
        
        if not plan_items:
            # Generate generic plan
            days_per_section = max(1, duration_days // 5)
            plan_items = [
                f"Day 1-{days_per_section}: Basics and fundamentals",
                f"Day {days_per_section+1}-{days_per_section*2}: Core concepts",
                f"Day {days_per_section*2+1}-{days_per_section*3}: Practical applications",
                f"Day {days_per_section*3+1}-{days_per_section*4}: Advanced topics",
                f"Day {days_per_section*4+1}-{duration_days}: Projects and practice"
            ]
        
        # Adjust for duration
        if duration_days != 14:
            # Simple scaling
            adjusted_items = []
            scale_factor = duration_days / 14
            
            for item in plan_items:
                # Extract day numbers and scale them
                import re
                day_match = re.search(r'Day (\d+)-(\d+)', item)
                if day_match:
                    start_day = max(1, int(int(day_match.group(1)) * scale_factor))
                    end_day = max(start_day, int(int(day_match.group(2)) * scale_factor))
                    content = item.split(': ', 1)[1] if ': ' in item else item
                    adjusted_items.append(f"Day {start_day}-{end_day}: {content}")
                else:
                    adjusted_items.append(item)
            
            plan_items = adjusted_items[:duration_days//2 + 1]  # Limit items
        
        # Create study plan
        result = [
            f"📖 STUDY PLAN: {topic.title()}",
            "=" * 50,
            f"Duration: {duration_days} days",
            f"Daily commitment: 1-2 hours recommended",
            "",
            "📅 Schedule:"
        ]
        
        for i, item in enumerate(plan_items, 1):
            result.append(f"{i:2d}. {item}")
        
        result.extend([
            "",
            "💡 Success Tips:",
            "• Set a consistent daily study time",
            "• Take notes and practice regularly", 
            "• Join online communities for support",
            "• Build projects to apply your learning",
            "• Review previous topics regularly"
        ])
        
        # Create a study file
        sandbox = get_sandbox()
        if sandbox:
            study_content = "\n".join(result)
            study_file = f"study_plan_{topic.replace(' ', '_')}.md"
            sandbox.create_file(study_file, study_content, "markdown")
        
        add_activity_log(f"Created {duration_days}-day study plan for {topic}")
        return "\n".join(result)
        
    except Exception as e:
        logger.error(f"Error creating study plan: {e}")
        return f"Error creating study plan: {str(e)}"

# ====================
# ENTERTAINMENT TOOLS
# ====================

@tool
async def tell_joke(category: str = "programming") -> str:
    """
    Tell a random joke to lighten the mood.
    
    Args:
        category: Type of joke (programming, general, dad, tech)
    
    Example prompts:
    - "Joke सुनाओ"
    - "हंसाओ मुझे"
    - "Programming joke बताओ"
    """
    try:
        jokes = {
            "programming": [
                "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
                "How many programmers does it take to change a light bulb? None, that's a hardware problem! 💡",
                "Why don't programmers like nature? It has too many bugs! 🌳",
                "What's a programmer's favorite hangout place? Foo Bar! 🍺",
                "Why did the programmer quit his job? He didn't get arrays! 📊"
            ],
            "general": [
                "Why don't scientists trust atoms? Because they make up everything! ⚛️",
                "Why did the math book look so sad? Because it had too many problems! 📚",
                "What do you call a bear with no teeth? A gummy bear! 🐻",
                "Why don't eggs tell jokes? They'd crack each other up! 🥚",
                "What's orange and sounds like a parrot? A carrot! 🥕"
            ],
            "dad": [
                "I'm reading a book about anti-gravity. It's impossible to put down! 📖",
                "Did you hear about the claustrophobic astronaut? He just needed some space! 🚀",
                "What do you call a fake noodle? An impasta! 🍝",
                "Why don't skeletons fight each other? They don't have the guts! 💀",
                "I used to hate facial hair, but then it grew on me! 🧔"
            ],
            "tech": [
                "Why was the computer cold? It left its Windows open! 🪟",
                "What did the WiFi router say to the device? 'You're not connected!' 📶",
                "Why did the smartphone go to therapy? It had too many apps-ues! 📱",
                "What's a computer's favorite snack? Microchips! 💻",
                "Why don't robots ever panic? They have great byte control! 🤖"
            ]
        }
        
        category_jokes = jokes.get(category, jokes["general"])
        selected_joke = random.choice(category_jokes)
        
        add_activity_log(f"Told a {category} joke")
        set_jarvis_state(JarvisState.SPEAKING, "Telling a joke...")
        
        return f"😄 Here's a {category} joke for you:\n\n{selected_joke}\n\nHope that made you smile! 😊"
        
    except Exception as e:
        logger.error(f"Error telling joke: {e}")
        return "I wanted to tell you a joke, but I seem to have forgotten it! Maybe my memory needs debugging! 🤖"

@tool
async def random_fact(category: str = "technology") -> str:
    """
    Share an interesting random fact.
    
    Args:
        category: Category of fact (technology, science, history, nature)
    
    Example prompts:
    - "Interesting fact बताओ"
    - "कुछ नया सिखाओ"
    - "Technology fact share करो"
    """
    try:
        facts = {
            "technology": [
                "🔍 The first computer bug was actually a real bug - a moth found in a Harvard computer in 1947!",
                "💾 The term 'byte' was coined by Werner Buchholz in 1956. It's a combination of 'bit' and 'bite'!",
                "🖥️ The first computer mouse was made of wood in 1964 by Douglas Engelbart!",
                "📱 Finland has more saunas than cars - about 2 million saunas for 5.5 million people!",
                "🌐 The @ symbol was used in email for the first time in 1971 by Ray Tomlinson!"
            ],
            "science": [
                "🧬 Humans share about 60% of their DNA with bananas!",
                "🌊 A group of flamingos is called a 'flamboyance'!",
                "⚡ Lightning strikes the Earth about 100 times per second!",
                "🧠 Your brain uses about 20% of your body's total energy!",
                "🔬 Honey never spoils - archaeologists have found edible honey in ancient tombs!"
            ],
            "history": [
                "🏛️ Oxford University is older than the Aztec Empire!",
                "📚 The Great Wall of China isn't visible from space with the naked eye!",
                "👑 Cleopatra lived closer in time to the moon landing than to the construction of the Great Pyramid!",
                "🗽 The Statue of Liberty was originally brown - it turned green due to oxidation!",
                "📜 Shakespeare invented over 1,700 words that we still use today!"
            ],
            "nature": [
                "🐙 Octopuses have three hearts and blue blood!",
                "🐘 Elephants can recognize themselves in mirrors - showing self-awareness!",
                "🌳 Trees can communicate with each other through underground fungal networks!",
                "🦆 Ducks have waterproof feathers - water literally rolls off their backs!",
                "🦎 Chameleons change color based on emotion and temperature, not just camouflage!"
            ]
        }
        
        category_facts = facts.get(category, facts["technology"])
        selected_fact = random.choice(category_facts)
        
        add_activity_log(f"Shared a {category} fact")
        set_jarvis_state(JarvisState.SPEAKING, "Sharing an interesting fact...")
        
        return f"🤔 Here's an interesting {category} fact:\n\n{selected_fact}\n\nPretty cool, right? Knowledge is power! 💡"
        
    except Exception as e:
        logger.error(f"Error sharing fact: {e}")
        return "I wanted to share a fascinating fact, but it seems to have slipped my digital mind! 🤖"

# ====================
# UTILITY TOOLS
# ====================

@tool
async def calculate_expression(expression: str) -> str:
    """
    Calculate mathematical expressions safely.
    
    Args:
        expression: Mathematical expression to evaluate
    
    Example prompts:
    - "Calculate 25 * 4 + 10"
    - "गणना करो 100 / 5"
    - "What is 15% of 200?"
    """
    try:
        set_jarvis_state(JarvisState.THINKING, "Calculating...")
        
        # Handle percentage calculations
        if "%" in expression:
            if " of " in expression.lower():
                parts = expression.lower().replace("%", "").split(" of ")
                if len(parts) == 2:
                    try:
                        percentage = float(parts[0].strip())
                        value = float(parts[1].strip())
                        result = (percentage / 100) * value
                        add_activity_log(f"Calculated: {percentage}% of {value} = {result}")
                        return f"🔢 {percentage}% of {value} = {result}"
                    except ValueError:
                        pass
        
        # Clean the expression for safety
        import re
        # Allow only numbers, operators, parentheses, and decimal points
        clean_expr = re.sub(r'[^0-9+\-*/().%\s]', '', expression)
        
        if not clean_expr.strip():
            return "❌ Invalid mathematical expression"
        
        # Replace % with /100 for percentage calculations
        clean_expr = clean_expr.replace('%', '/100')
        
        try:
            # Safely evaluate the expression
            result = eval(clean_expr)
            
            # Format result nicely
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)  # Round to 6 decimal places
            
            add_activity_log(f"Calculated: {expression} = {result}")
            return f"🔢 {expression} = {result}"
            
        except ZeroDivisionError:
            return "❌ Cannot divide by zero!"
        except Exception as e:
            return f"❌ Error in calculation: {str(e)}"
            
    except Exception as e:
        logger.error(f"Error in calculation: {e}")
        return f"Error calculating expression: {str(e)}"

@tool
async def unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert between different units of measurement.
    
    Args:
        value: Numeric value to convert
        from_unit: Source unit (e.g., 'celsius', 'km', 'kg')
        to_unit: Target unit (e.g., 'fahrenheit', 'miles', 'pounds')
    
    Example prompts:
    - "Convert 100 celsius to fahrenheit"
    - "25 km को miles में convert करो"
    - "How much is 5 kg in pounds?"
    """
    try:
        set_jarvis_state(JarvisState.THINKING, f"Converting {value} {from_unit} to {to_unit}...")
        
        conversions = {
            # Temperature
            ("celsius", "fahrenheit"): lambda x: (x * 9/5) + 32,
            ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
            ("celsius", "kelvin"): lambda x: x + 273.15,
            ("kelvin", "celsius"): lambda x: x - 273.15,
            
            # Length
            ("km", "miles"): lambda x: x * 0.621371,
            ("miles", "km"): lambda x: x / 0.621371,
            ("meters", "feet"): lambda x: x * 3.28084,
            ("feet", "meters"): lambda x: x / 3.28084,
            ("cm", "inches"): lambda x: x * 0.393701,
            ("inches", "cm"): lambda x: x / 0.393701,
            
            # Weight
            ("kg", "pounds"): lambda x: x * 2.20462,
            ("pounds", "kg"): lambda x: x / 2.20462,
            ("grams", "ounces"): lambda x: x * 0.035274,
            ("ounces", "grams"): lambda x: x / 0.035274,
            
            # Volume
            ("liters", "gallons"): lambda x: x * 0.264172,
            ("gallons", "liters"): lambda x: x / 0.264172,
            ("ml", "cups"): lambda x: x * 0.00422675,
            ("cups", "ml"): lambda x: x / 0.00422675,
        }
        
        # Normalize unit names
        from_unit = from_unit.lower().strip()
        to_unit = to_unit.lower().strip()
        
        # Find conversion function
        conversion_key = (from_unit, to_unit)
        if conversion_key in conversions:
            result = conversions[conversion_key](value)
            result = round(result, 4)  # Round to 4 decimal places
            
            add_activity_log(f"Converted: {value} {from_unit} = {result} {to_unit}")
            return f"🔄 {value} {from_unit} = {result} {to_unit}"
        
        # Check if reverse conversion exists
        reverse_key = (to_unit, from_unit)
        if reverse_key in conversions:
            # Use inverse of reverse function
            reverse_func = conversions[reverse_key]
            # For simple linear conversions, we can invert
            try:
                # This is a simplified approach - doesn't work for all functions
                test_val = reverse_func(1)
                if test_val != 0:
                    result = value / test_val
                    result = round(result, 4)
                    add_activity_log(f"Converted: {value} {from_unit} = {result} {to_unit}")
                    return f"🔄 {value} {from_unit} = {result} {to_unit}"
            except:
                pass
        
        # If no conversion found, list available conversions
        available_conversions = []
        for (f, t) in conversions.keys():
            if f == from_unit:
                available_conversions.append(t)
        
        if available_conversions:
            return f"❌ Cannot convert {from_unit} to {to_unit}. Available conversions from {from_unit}: {', '.join(available_conversions)}"
        else:
            return f"❌ Conversion not supported. Supported units: celsius, fahrenheit, km, miles, kg, pounds, liters, gallons, etc."
            
    except Exception as e:
        logger.error(f"Error in unit conversion: {e}")
        return f"Error converting units: {str(e)}"

@tool 
async def generate_password(length: int = 12, include_symbols: bool = True) -> str:
    """
    Generate a secure random password.
    
    Args:
        length: Password length (default 12)
        include_symbols: Whether to include special symbols
    
    Example prompts:
    - "Strong password generate करो"
    - "16 character का password बनाओ"
    - "Secure password चाहिए without symbols"
    """
    try:
        import string
        import secrets
        
        # Character sets
        letters = string.ascii_letters  # a-z, A-Z
        digits = string.digits  # 0-9
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if include_symbols else ""
        
        # Ensure minimum requirements
        length = max(6, min(length, 50))  # Between 6 and 50 characters
        
        # Build character pool
        char_pool = letters + digits
        if include_symbols:
            char_pool += symbols
        
        # Generate password ensuring at least one of each type
        password = []
        
        # Ensure at least one of each required type
        password.append(secrets.choice(string.ascii_lowercase))  # lowercase
        password.append(secrets.choice(string.ascii_uppercase))  # uppercase  
        password.append(secrets.choice(digits))  # digit
        
        if include_symbols:
            password.append(secrets.choice(symbols))  # symbol
        
        # Fill remaining length with random characters
        remaining_length = length - len(password)
        for _ in range(remaining_length):
            password.append(secrets.choice(char_pool))
        
        # Shuffle the password list
        secrets.SystemRandom().shuffle(password)
        
        # Convert to string
        final_password = ''.join(password)
        
        # Security tips
        tips = [
            "🔐 Password Security Tips:",
            "• Never share your password with anyone",
            "• Use different passwords for different accounts", 
            "• Consider using a password manager",
            "• Enable two-factor authentication when possible"
        ]
        
        result = [
            f"🔑 Generated Password ({length} characters):",
            "=" * 40,
            final_password,
            "",
            "\n".join(tips)
        ]
        
        add_activity_log(f"Generated {length}-character password")
        return "\n".join(result)
        
    except Exception as e:
        logger.error(f"Error generating password: {e}")
        return f"Error generating password: {str(e)}"