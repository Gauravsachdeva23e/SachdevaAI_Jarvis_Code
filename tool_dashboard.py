"""
Tool Management Dashboard for Jarvis AI Assistant
Provides comprehensive overview and management of all available tools
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

from tool_orchestrator import get_orchestrator, ToolCategory
from jarvis_visual import add_activity_log, set_jarvis_state, JarvisState

logger = logging.getLogger(__name__)

class ToolDashboard:
    """Interactive dashboard for managing Jarvis tools"""
    
    def __init__(self, master=None):
        if master is None:
            self.root = tk.Tk()
        else:
            self.root = master
            
        self.orchestrator = get_orchestrator()
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup the dashboard UI"""
        self.root.title("Jarvis Tool Management Dashboard")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1e1e1e')
        
        # Create main notebook for tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1e1e1e')
        style.configure('TNotebook.Tab', background='#2d2d2d', foreground='white')
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_overview_tab()
        self.create_tools_tab()
        self.create_usage_tab()
        self.create_test_tab()
        
    def create_overview_tab(self):
        """Create overview tab"""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="📊 Overview")
        
        # Title
        title_label = tk.Label(
            overview_frame, 
            text="🤖 Jarvis AI Assistant - Tool Dashboard",
            font=('Arial', 18, 'bold'),
            bg='#1e1e1e',
            fg='#00ff00'
        )
        title_label.pack(pady=10)
        
        # Stats frame
        stats_frame = tk.Frame(overview_frame, bg='#1e1e1e')
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        # Tool categories stats
        categories_frame = tk.LabelFrame(
            stats_frame,
            text="📂 Tool Categories",
            font=('Arial', 12, 'bold'),
            bg='#2d2d2d',
            fg='white'
        )
        categories_frame.pack(fill='x', pady=5)
        
        self.category_labels = {}
        row = 0
        col = 0
        for category in ToolCategory:
            count = sum(1 for tool in self.orchestrator.tool_registry.values() 
                       if tool.category == category)
            
            category_label = tk.Label(
                categories_frame,
                text=f"{category.value.replace('_', ' ').title()}: {count}",
                font=('Consolas', 10),
                bg='#2d2d2d',
                fg='#00bfff'
            )
            category_label.grid(row=row, column=col, padx=10, pady=2, sticky='w')
            self.category_labels[category] = category_label
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # System status
        status_frame = tk.LabelFrame(
            stats_frame,
            text="⚡ System Status",
            font=('Arial', 12, 'bold'),
            bg='#2d2d2d',
            fg='white'
        )
        status_frame.pack(fill='x', pady=5)
        
        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            height=8,
            bg='#1a1a1a',
            fg='#00ff00',
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.status_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Control buttons
        button_frame = tk.Frame(overview_frame, bg='#1e1e1e')
        button_frame.pack(fill='x', padx=20, pady=10)
        
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_data,
            bg='#0066cc',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='raised'
        )
        refresh_btn.pack(side='left', padx=5)
        
        test_btn = tk.Button(
            button_frame,
            text="🧪 Run Tests",
            command=self.run_tool_tests,
            bg='#cc6600',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='raised'
        )
        test_btn.pack(side='left', padx=5)
        
    def create_tools_tab(self):
        """Create tools management tab"""
        tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(tools_frame, text="🛠️ Tools")
        
        # Search frame
        search_frame = tk.Frame(tools_frame, bg='#1e1e1e')
        search_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            search_frame,
            text="🔍 Search:",
            bg='#1e1e1e',
            fg='white',
            font=('Arial', 10)
        ).pack(side='left', padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_tools)
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg='#2d2d2d',
            fg='white',
            font=('Consolas', 10),
            width=30
        )
        search_entry.pack(side='left', padx=5)
        
        # Category filter
        tk.Label(
            search_frame,
            text="📂 Category:",
            bg='#1e1e1e',
            fg='white',
            font=('Arial', 10)
        ).pack(side='left', padx=(20, 5))
        
        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(
            search_frame,
            textvariable=self.category_var,
            values=["All"] + [cat.value.replace('_', ' ').title() for cat in ToolCategory],
            width=20
        )
        category_combo.pack(side='left', padx=5)
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_tools())
        
        # Tools treeview
        tree_frame = tk.Frame(tools_frame, bg='#1e1e1e')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('Name', 'Category', 'Priority', 'Description')
        self.tools_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tools_tree.heading('Name', text='Tool Name')
        self.tools_tree.heading('Category', text='Category')
        self.tools_tree.heading('Priority', text='Priority')
        self.tools_tree.heading('Description', text='Description')
        
        self.tools_tree.column('Name', width=200)
        self.tools_tree.column('Category', width=150)
        self.tools_tree.column('Priority', width=80)
        self.tools_tree.column('Description', width=400)
        
        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tools_tree.yview)
        self.tools_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tools_tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')
        
        # Tool details frame
        details_frame = tk.LabelFrame(
            tools_frame,
            text="🔍 Tool Details",
            font=('Arial', 12, 'bold'),
            bg='#2d2d2d',
            fg='white'
        )
        details_frame.pack(fill='x', padx=10, pady=5)
        
        self.tool_details = scrolledtext.ScrolledText(
            details_frame,
            height=6,
            bg='#1a1a1a',
            fg='#cccccc',
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.tool_details.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Bind selection event
        self.tools_tree.bind('<<TreeviewSelect>>', self.on_tool_select)
        
    def create_usage_tab(self):
        """Create usage statistics tab"""
        usage_frame = ttk.Frame(self.notebook)
        self.notebook.add(usage_frame, text="📈 Usage")
        
        # Usage statistics will be displayed here
        usage_text = scrolledtext.ScrolledText(
            usage_frame,
            bg='#1a1a1a',
            fg='#cccccc',
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        usage_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sample usage data
        usage_data = """
📊 JARVIS TOOL USAGE STATISTICS
==============================

🔥 Most Used Tools:
1. google_search - 45 uses
2. get_weather - 32 uses  
3. open_app - 28 uses
4. write_code - 24 uses
5. get_system_info - 19 uses

📂 Usage by Category:
• Web Search: 52 uses (25.4%)
• System Info: 48 uses (23.5%) 
• Code Development: 42 uses (20.6%)
• File Management: 35 uses (17.1%)
• Automation: 28 uses (13.7%)

⏱️ Peak Usage Hours:
• 9:00-11:00 AM: 35%
• 2:00-4:00 PM: 28%
• 7:00-9:00 PM: 22%

🎯 Success Rate: 94.2%
⚡ Average Response Time: 1.3 seconds
📅 Total Sessions: 156
🔄 Tools Executed: 204
        """
        
        usage_text.insert('1.0', usage_data)
        usage_text.configure(state='disabled')
        
    def create_test_tab(self):
        """Create tool testing tab"""
        test_frame = ttk.Frame(self.notebook)
        self.notebook.add(test_frame, text="🧪 Testing")
        
        # Test input frame
        input_frame = tk.LabelFrame(
            test_frame,
            text="🎯 Test Tool",
            font=('Arial', 12, 'bold'),
            bg='#2d2d2d',
            fg='white'
        )
        input_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            input_frame,
            text="Query:",
            bg='#2d2d2d',
            fg='white',
            font=('Arial', 10)
        ).pack(anchor='w', padx=5, pady=2)
        
        self.test_query = tk.Entry(
            input_frame,
            bg='#1a1a1a',
            fg='white',
            font=('Consolas', 11),
            width=80
        )
        self.test_query.pack(fill='x', padx=5, pady=2)
        
        # Test button
        test_execute_btn = tk.Button(
            input_frame,
            text="▶️ Execute Test",
            command=self.execute_test,
            bg='#00aa00',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='raised'
        )
        test_execute_btn.pack(pady=5)
        
        # Results frame
        results_frame = tk.LabelFrame(
            test_frame,
            text="📋 Test Results",
            font=('Arial', 12, 'bold'),
            bg='#2d2d2d',
            fg='white'
        )
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.test_results = scrolledtext.ScrolledText(
            results_frame,
            bg='#1a1a1a',
            fg='#00ff00',
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.test_results.pack(fill='both', expand=True, padx=5, pady=5)
        
    def refresh_data(self):
        """Refresh dashboard data"""
        self.update_overview()
        self.update_tools_list()
        self.log_status("📊 Dashboard data refreshed")
        
    def update_overview(self):
        """Update overview statistics"""
        total_tools = len(self.orchestrator.tool_registry)
        
        status_info = f"""
🤖 JARVIS AI ASSISTANT STATUS
============================
⚡ Status: Online and Ready
🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🛠️  Total Tools: {total_tools}
🧠 Orchestrator: Active
👀 Visual Interface: Active
🔒 Sandbox: Ready

🎯 TOOL CATEGORIES LOADED:
"""
        
        for category in ToolCategory:
            count = sum(1 for tool in self.orchestrator.tool_registry.values() 
                       if tool.category == category)
            if count > 0:
                emoji_map = {
                    'SYSTEM_INFO': '💻',
                    'FILE_MANAGEMENT': '📁', 
                    'CODE_DEVELOPMENT': '👨‍💻',
                    'WEB_SEARCH': '🔍',
                    'COMMUNICATION': '💬',
                    'AUTOMATION': '🤖',
                    'MULTIMEDIA': '🎵',
                    'PRODUCTIVITY': '📊',
                    'LEARNING': '📚',
                    'ENTERTAINMENT': '🎮',
                    'UTILITIES': '🔧'
                }
                emoji = emoji_map.get(category.name, '⚙️')
                status_info += f"{emoji} {category.value.replace('_', ' ').title()}: {count} tools\n"
        
        self.status_text.delete('1.0', tk.END)
        self.status_text.insert('1.0', status_info)
        
    def update_tools_list(self):
        """Update tools list"""
        # Clear existing items
        for item in self.tools_tree.get_children():
            self.tools_tree.delete(item)
        
        # Add all tools
        for tool_name, metadata in self.orchestrator.tool_registry.items():
            priority_text = f"{metadata.priority}/10"
            description = metadata.description[:80] + "..." if len(metadata.description) > 80 else metadata.description
            
            self.tools_tree.insert('', 'end', values=(
                tool_name,
                metadata.category.value.replace('_', ' ').title(),
                priority_text,
                description
            ))
    
    def filter_tools(self, *args):
        """Filter tools based on search and category"""
        search_text = self.search_var.get().lower()
        selected_category = self.category_var.get()
        
        # Clear existing items
        for item in self.tools_tree.get_children():
            self.tools_tree.delete(item)
        
        # Add filtered tools
        for tool_name, metadata in self.orchestrator.tool_registry.items():
            # Category filter
            if selected_category != "All":
                tool_category = metadata.category.value.replace('_', ' ').title()
                if tool_category != selected_category:
                    continue
            
            # Search filter
            if search_text:
                if (search_text not in tool_name.lower() and 
                    search_text not in metadata.description.lower() and
                    not any(search_text in keyword.lower() for keyword in metadata.keywords)):
                    continue
            
            priority_text = f"{metadata.priority}/10"
            description = metadata.description[:80] + "..." if len(metadata.description) > 80 else metadata.description
            
            self.tools_tree.insert('', 'end', values=(
                tool_name,
                metadata.category.value.replace('_', ' ').title(),
                priority_text,
                description
            ))
    
    def on_tool_select(self, event):
        """Handle tool selection"""
        selection = self.tools_tree.selection()
        if selection:
            item = self.tools_tree.item(selection[0])
            tool_name = item['values'][0]
            
            if tool_name in self.orchestrator.tool_registry:
                metadata = self.orchestrator.tool_registry[tool_name]
                
                details = f"""
🛠️ TOOL: {tool_name}
{'=' * 50}
📂 Category: {metadata.category.value.replace('_', ' ').title()}
⭐ Priority: {metadata.priority}/10
⏱️  Estimated Time: {metadata.estimated_time}s
🔒 Min Confidence: {metadata.min_confidence}
⚡ Async Capable: {'Yes' if metadata.async_capable else 'No'}

📝 Description:
{metadata.description}

🏷️ Keywords:
{', '.join(metadata.keywords)}

⚙️ Prerequisites:
{', '.join(metadata.prerequisites) if metadata.prerequisites else 'None'}

⚠️ Conflicts:
{', '.join(metadata.conflicts) if metadata.conflicts else 'None'}
"""
                
                self.tool_details.delete('1.0', tk.END)
                self.tool_details.insert('1.0', details)
    
    def execute_test(self):
        """Execute a test query"""
        query = self.test_query.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a test query")
            return
        
        self.test_results.delete('1.0', tk.END)
        self.test_results.insert('1.0', f"🧪 Testing query: {query}\n{'=' * 50}\n")
        self.test_results.update()
        
        def run_test():
            try:
                # Analyze the query
                analysis = self.orchestrator.analyze_query(query)
                
                self.test_results.insert(tk.END, f"\n🧠 INTENT ANALYSIS:\n")
                for intent, confidence in analysis['intents'].items():
                    self.test_results.insert(tk.END, f"• {intent}: {confidence:.2f}\n")
                
                self.test_results.insert(tk.END, f"\n🎯 MATCHING TOOLS:\n")
                for tool_name, metadata, score in analysis['matching_tools']:
                    self.test_results.insert(tk.END, f"• {tool_name} (score: {score:.2f})\n")
                
                # Select tools
                selected_tools = self.orchestrator.select_tools(analysis)
                self.test_results.insert(tk.END, f"\n✅ SELECTED TOOLS:\n")
                for tool_name, metadata in selected_tools:
                    self.test_results.insert(tk.END, f"• {tool_name} ({metadata.category.value})\n")
                
                self.test_results.insert(tk.END, f"\n🏁 Test completed successfully!")
                
            except Exception as e:
                self.test_results.insert(tk.END, f"\n❌ Test failed: {str(e)}")
            
            self.test_results.see(tk.END)
        
        # Run in separate thread to avoid blocking UI
        threading.Thread(target=run_test, daemon=True).start()
    
    def run_tool_tests(self):
        """Run comprehensive tool tests"""
        def run_tests():
            test_queries = [
                "What time is it?",
                "System information बताओ",
                "VS Code खोलो",
                "Weather check करो",
                "Task बनाओ - Complete project",
                "Joke सुनाओ",
                "Calculate 25 * 4"
            ]
            
            self.status_text.delete('1.0', tk.END)
            self.status_text.insert('1.0', "🧪 Running comprehensive tool tests...\n" + "=" * 40 + "\n\n")
            
            passed = 0
            total = len(test_queries)
            
            for i, query in enumerate(test_queries, 1):
                try:
                    self.status_text.insert(tk.END, f"Test {i}/{total}: {query}\n")
                    self.status_text.update()
                    
                    analysis = self.orchestrator.analyze_query(query)
                    tools = self.orchestrator.select_tools(analysis)
                    
                    if tools:
                        self.status_text.insert(tk.END, f"✅ Found {len(tools)} matching tools\n")
                        passed += 1
                    else:
                        self.status_text.insert(tk.END, f"❌ No tools matched\n")
                    
                    self.status_text.insert(tk.END, "\n")
                    
                except Exception as e:
                    self.status_text.insert(tk.END, f"❌ Error: {str(e)}\n\n")
            
            success_rate = (passed / total) * 100
            self.status_text.insert(tk.END, f"\n🎯 Test Results: {passed}/{total} passed ({success_rate:.1f}%)\n")
            self.status_text.see(tk.END)
        
        threading.Thread(target=run_tests, daemon=True).start()
    
    def log_status(self, message: str):
        """Log status message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # Add to status text
        self.status_text.insert(tk.END, log_message)
        self.status_text.see(tk.END)
        
        # Also add to visual interface if available
        try:
            add_activity_log(message)
        except:
            pass
    
    def run(self):
        """Run the dashboard"""
        self.root.mainloop()

def launch_dashboard():
    """Launch the tool dashboard"""
    dashboard = ToolDashboard()
    dashboard.run()

if __name__ == "__main__":
    launch_dashboard()