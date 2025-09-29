"""
Advanced Coding Tools for Jarvis AI Assistant
Provides intelligent code generation, debugging, and development utilities
"""

import ast
import re
import os
import subprocess
import tempfile
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from langchain.tools import tool

from jarvis_visual import add_activity_log, set_jarvis_state, JarvisState
from vscode_sandbox import get_sandbox

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """Analyzes and improves code quality"""
    
    def __init__(self):
        self.python_keywords = {
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except',
            'finally', 'with', 'import', 'from', 'return', 'yield', 'lambda',
            'and', 'or', 'not', 'in', 'is', 'None', 'True', 'False'
        }
    
    def analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code for errors and improvements"""
        analysis = {
            'syntax_errors': [],
            'style_issues': [],
            'suggestions': [],
            'complexity_score': 0,
            'is_valid': True
        }
        
        try:
            # Check syntax
            ast.parse(code)
            analysis['suggestions'].append("✅ Syntax is valid")
        except SyntaxError as e:
            analysis['syntax_errors'].append(f"Syntax Error: {e.msg} at line {e.lineno}")
            analysis['is_valid'] = False
        
        # Analyze code style and structure
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for common style issues
            if line and not line_stripped:
                continue  # Skip empty lines
                
            # Indentation check
            if line.startswith(' ') and not line.startswith('    '):
                analysis['style_issues'].append(f"Line {i}: Inconsistent indentation (use 4 spaces)")
            
            # Line length check
            if len(line) > 100:
                analysis['style_issues'].append(f"Line {i}: Line too long ({len(line)} chars)")
            
            # Check for missing spaces around operators
            if re.search(r'[a-zA-Z0-9]\+[a-zA-Z0-9]', line):
                analysis['style_issues'].append(f"Line {i}: Missing spaces around '+' operator")
            
            if re.search(r'[a-zA-Z0-9]\=[a-zA-Z0-9]', line):
                analysis['style_issues'].append(f"Line {i}: Missing spaces around '=' operator")
        
        # Calculate complexity (simple metric)
        complexity_indicators = ['if', 'for', 'while', 'try', 'def', 'class']
        analysis['complexity_score'] = sum(code.count(keyword) for keyword in complexity_indicators)
        
        # Add suggestions based on analysis
        if analysis['complexity_score'] > 10:
            analysis['suggestions'].append("⚠️ High complexity - consider breaking into smaller functions")
        
        if len(lines) > 50:
            analysis['suggestions'].append("📝 Large file - consider splitting into modules")
            
        return analysis
    
    def fix_python_code(self, code: str) -> str:
        """Automatically fix common Python code issues"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix spacing around operators
            line = re.sub(r'([a-zA-Z0-9_])\+([a-zA-Z0-9_])', r'\1 + \2', line)
            line = re.sub(r'([a-zA-Z0-9_])\-([a-zA-Z0-9_])', r'\1 - \2', line)
            line = re.sub(r'([a-zA-Z0-9_])\*([a-zA-Z0-9_])', r'\1 * \2', line)
            line = re.sub(r'([a-zA-Z0-9_])\=([a-zA-Z0-9_])', r'\1 = \2', line)
            
            # Fix function definitions
            line = re.sub(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', r'def \1(', line)
            
            # Fix class definitions
            line = re.sub(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', r'class \1(', line)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

class CodeGenerator:
    """Generates code templates and boilerplate"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load code templates"""
        return {
            'python': {
                'function': '''def {name}({params}):
    \"\"\"
    {description}
    
    Args:
        {args_doc}
    
    Returns:
        {return_doc}
    \"\"\"
    {body}
    return {return_value}''',
                
                'class': '''class {name}:
    \"\"\"
    {description}
    \"\"\"
    
    def __init__(self{init_params}):
        \"\"\"Initialize {name}\"\"\"
        {init_body}
    
    def {method_name}(self{method_params}):
        \"\"\"
        {method_description}
        \"\"\"
        {method_body}''',
                
                'flask_app': '''from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    \"\"\"Home endpoint\"\"\"
    return jsonify({{
        "message": "Hello from {app_name}!",
        "status": "success"
    }})

@app.route('/api/{endpoint}', methods=['GET', 'POST'])
def {endpoint}_handler():
    \"\"\"Handle {endpoint} requests\"\"\"
    if request.method == 'GET':
        return jsonify({{"data": "GET response"}})
    elif request.method == 'POST':
        data = request.get_json()
        return jsonify({{"received": data, "status": "processed"}})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)''',
                
                'fastapi_app': '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="{app_name}", version="1.0.0")

class {model_name}(BaseModel):
    {model_fields}

@app.get("/")
async def root():
    \"\"\"Root endpoint\"\"\"
    return {{"message": "Hello from {app_name}!"}}

@app.get("/api/{endpoint}")
async def get_{endpoint}():
    \"\"\"Get {endpoint} data\"\"\"
    return {{"data": "sample data"}}

@app.post("/api/{endpoint}")
async def create_{endpoint}(item: {model_name}):
    \"\"\"Create new {endpoint}\"\"\"
    return {{"status": "created", "item": item}}''',
                
                'data_analysis': '''import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def load_data(file_path: str) -> pd.DataFrame:
    \"\"\"Load data from file\"\"\"
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format")
    except Exception as e:
        print(f"Error loading data: {{e}}")
        return pd.DataFrame()

def analyze_data(df: pd.DataFrame):
    \"\"\"Basic data analysis\"\"\"
    print("Dataset Info:")
    print(f"Shape: {{df.shape}}")
    print(f"Columns: {{list(df.columns)}}")
    print("\\nBasic Statistics:")
    print(df.describe())
    print("\\nMissing Values:")
    print(df.isnull().sum())

def visualize_data(df: pd.DataFrame, target_column: str = None):
    \"\"\"Create visualizations\"\"\"
    plt.figure(figsize=(12, 8))
    
    # Correlation heatmap
    plt.subplot(2, 2, 1)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm')
    plt.title('Correlation Heatmap')
    
    # Distribution plots
    plt.subplot(2, 2, 2)
    if target_column and target_column in df.columns:
        df[target_column].hist(bins=30)
        plt.title(f'Distribution of {{target_column}}')
    
    plt.tight_layout()
    plt.show()

# Main execution
if __name__ == "__main__":
    # Load and analyze data
    df = load_data("{data_file}")
    if not df.empty:
        analyze_data(df)
        visualize_data(df, "{target_column}")'''
            },
            
            'javascript': {
                'function': '''/**
 * {description}
 * @param {{{param_types}}} {params}
 * @returns {{{return_type}}} {return_description}
 */
function {name}({params}) {{
    {body}
    return {return_value};
}}''',
                
                'class': '''/**
 * {description}
 */
class {name} {{
    constructor({constructor_params}) {{
        {constructor_body}
    }}
    
    /**
     * {method_description}
     * @param {{{method_param_types}}} {method_params}
     * @returns {{{method_return_type}}}
     */
    {method_name}({method_params}) {{
        {method_body}
    }}
}}''',
                
                'express_app': '''const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({{ extended: true }}));

// Routes
app.get('/', (req, res) => {{
    res.json({{
        message: 'Welcome to {app_name}!',
        status: 'success',
        timestamp: new Date().toISOString()
    }});
}});

app.get('/api/{endpoint}', (req, res) => {{
    res.json({{
        data: 'Sample data for {endpoint}',
        status: 'success'
    }});
}});

app.post('/api/{endpoint}', (req, res) => {{
    const data = req.body;
    res.json({{
        message: 'Data received successfully',
        received: data,
        status: 'success'
    }});
}});

// Error handling middleware
app.use((err, req, res, next) => {{
    console.error(err.stack);
    res.status(500).json({{
        message: 'Something went wrong!',
        status: 'error'
    }});
}});

// Start server
app.listen(PORT, () => {{
    console.log(`Server is running on port ${{PORT}}`);
}});'''
            },
            
            'html': {
                'webpage': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        .content {{
            line-height: 1.6;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="content">
            <p>{content}</p>
        </div>
    </div>
    
    <script>
        // JavaScript functionality
        console.log('Page loaded successfully!');
        {javascript_code}
    </script>
</body>
</html>'''
            }
        }
    
    def generate_code(self, template_type: str, language: str, **kwargs) -> str:
        """Generate code from template"""
        try:
            template = self.templates.get(language, {}).get(template_type, "")
            if not template:
                return f"# Template '{template_type}' not found for {language}"
            
            return template.format(**kwargs)
        except KeyError as e:
            return f"# Missing parameter: {e}"
        except Exception as e:
            return f"# Error generating code: {e}"

# Global instances
_code_analyzer = CodeAnalyzer()
_code_generator = CodeGenerator()

@tool
async def analyze_code(code: str, language: str = "python") -> str:
    """
    Analyze code for errors, style issues, and improvements.
    
    Args:
        code: The code to analyze
        language: Programming language (currently supports python)
    
    Use this to check code quality and get improvement suggestions.
    """
    try:
        set_jarvis_state(JarvisState.THINKING, "Analyzing code...")
        
        if language.lower() == "python":
            analysis = _code_analyzer.analyze_python_code(code)
            
            result = ["📊 CODE ANALYSIS REPORT", "=" * 30]
            
            if analysis['syntax_errors']:
                result.append("🚨 SYNTAX ERRORS:")
                result.extend([f"  • {error}" for error in analysis['syntax_errors']])
                result.append("")
            
            if analysis['style_issues']:
                result.append("⚠️  STYLE ISSUES:")
                result.extend([f"  • {issue}" for issue in analysis['style_issues']])
                result.append("")
            
            result.append("💡 SUGGESTIONS:")
            if analysis['suggestions']:
                result.extend([f"  • {suggestion}" for suggestion in analysis['suggestions']])
            else:
                result.append("  • Code looks good!")
            
            result.append(f"\\n📈 COMPLEXITY SCORE: {analysis['complexity_score']}")
            result.append(f"✅ VALID SYNTAX: {analysis['is_valid']}")
            
            add_activity_log(f"Code analysis completed - {len(analysis['syntax_errors'])} errors, {len(analysis['style_issues'])} style issues")
            return "\\n".join(result)
        
        else:
            return f"Code analysis for {language} is not yet supported."
            
    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        return f"Error during code analysis: {str(e)}"

@tool
async def fix_code(code: str, language: str = "python") -> str:
    """
    Automatically fix common code issues and improve formatting.
    
    Args:
        code: The code to fix
        language: Programming language
    
    Use this to automatically fix formatting and common issues.
    """
    try:
        set_jarvis_state(JarvisState.THINKING, "Fixing code issues...")
        
        if language.lower() == "python":
            fixed_code = _code_analyzer.fix_python_code(code)
            add_activity_log("Python code formatting fixed")
            
            return f"🔧 FIXED CODE:\\n{'-' * 40}\\n{fixed_code}"
        
        else:
            return f"Code fixing for {language} is not yet supported."
            
    except Exception as e:
        logger.error(f"Error fixing code: {e}")
        return f"Error fixing code: {str(e)}"

@tool
async def generate_function(name: str, description: str, parameters: str = "", return_type: str = "None", language: str = "python") -> str:
    """
    Generate a function template with proper documentation.
    
    Args:
        name: Function name
        description: What the function does
        parameters: Function parameters (e.g., "x: int, y: str")
        return_type: Return type description
        language: Programming language
    
    Example prompts:
    - "Calculator function बनाओ"
    - "Data processing function generate करो"
    """
    try:
        set_jarvis_state(JarvisState.WRITING, f"Generating {name} function...")
        
        if language.lower() == "python":
            # Parse parameters
            if parameters:
                param_list = [p.strip() for p in parameters.split(',')]
                args_doc = "\\n        ".join([f"{p}: Description for {p.split(':')[0]}" for p in param_list])
            else:
                param_list = []
                args_doc = "None"
            
            function_code = _code_generator.generate_code(
                'function', 'python',
                name=name,
                params=parameters or "",
                description=description,
                args_doc=args_doc,
                return_doc=return_type,
                body=f"    # TODO: Implement {name}\\n    pass",
                return_value="None"
            )
            
        elif language.lower() == "javascript":
            function_code = _code_generator.generate_code(
                'function', 'javascript',
                name=name,
                params=parameters or "",
                description=description,
                param_types="Object",
                return_type=return_type,
                return_description=f"Result of {name}",
                body=f"    // TODO: Implement {name}",
                return_value="null"
            )
        
        else:
            return f"Function generation for {language} is not yet supported."
        
        # Write to VS Code if available
        sandbox = get_sandbox()
        if sandbox:
            sandbox.safe_write_text(function_code)
        
        add_activity_log(f"Generated {name} function template")
        return f"✅ Generated {name} function:\\n{function_code}"
        
    except Exception as e:
        logger.error(f"Error generating function: {e}")
        return f"Error generating function: {str(e)}"

@tool
async def generate_class(name: str, description: str, methods: str = "process", language: str = "python") -> str:
    """
    Generate a class template with methods and documentation.
    
    Args:
        name: Class name
        description: What the class does
        methods: Comma-separated method names
        language: Programming language
    
    Example prompts:
    - "User class बनाओ"
    - "Data handler class generate करो"
    """
    try:
        set_jarvis_state(JarvisState.WRITING, f"Generating {name} class...")
        
        method_list = [m.strip() for m in methods.split(',')]
        primary_method = method_list[0] if method_list else "process"
        
        if language.lower() == "python":
            class_code = _code_generator.generate_code(
                'class', 'python',
                name=name,
                description=description,
                init_params="",
                init_body="        pass",
                method_name=primary_method,
                method_params="",
                method_description=f"{primary_method} method for {name}",
                method_body=f"        # TODO: Implement {primary_method}\\n        pass"
            )
        
        elif language.lower() == "javascript":
            class_code = _code_generator.generate_code(
                'class', 'javascript',
                name=name,
                description=description,
                constructor_params="",
                constructor_body="        // Initialize class",
                method_name=primary_method,
                method_params="",
                method_description=f"{primary_method} method",
                method_param_types="Object",
                method_return_type="Object",
                method_body=f"        // TODO: Implement {primary_method}"
            )
        
        else:
            return f"Class generation for {language} is not yet supported."
        
        # Write to VS Code if available
        sandbox = get_sandbox()
        if sandbox:
            sandbox.safe_write_text(class_code)
        
        add_activity_log(f"Generated {name} class template")
        return f"✅ Generated {name} class:\\n{class_code}"
        
    except Exception as e:
        logger.error(f"Error generating class: {e}")
        return f"Error generating class: {str(e)}"

@tool
async def create_web_app(app_name: str, framework: str = "flask", endpoints: str = "users,posts") -> str:
    """
    Generate a complete web application template.
    
    Args:
        app_name: Name of the application
        framework: Web framework (flask, fastapi, express)
        endpoints: Comma-separated list of API endpoints
    
    Example prompts:
    - "Flask web app बनाओ"
    - "API server create करो"
    - "Express.js application generate करो"
    """
    try:
        set_jarvis_state(JarvisState.WRITING, f"Creating {framework} web app...")
        
        endpoint_list = [e.strip() for e in endpoints.split(',')]
        primary_endpoint = endpoint_list[0] if endpoint_list else "data"
        
        if framework.lower() == "flask":
            app_code = _code_generator.generate_code(
                'flask_app', 'python',
                app_name=app_name,
                endpoint=primary_endpoint
            )
        
        elif framework.lower() == "fastapi":
            app_code = _code_generator.generate_code(
                'fastapi_app', 'python',
                app_name=app_name,
                endpoint=primary_endpoint,
                model_name=f"{primary_endpoint.capitalize()}Item",
                model_fields="id: int\\n    name: str\\n    description: Optional[str] = None"
            )
        
        elif framework.lower() == "express":
            app_code = _code_generator.generate_code(
                'express_app', 'javascript',
                app_name=app_name,
                endpoint=primary_endpoint
            )
        
        else:
            return f"Web app generation for {framework} is not yet supported."
        
        # Create file in sandbox
        sandbox = get_sandbox()
        if framework in ["flask", "fastapi"]:
            filename = f"{app_name.lower()}_app.py"
        else:
            filename = f"{app_name.lower()}_app.js"
        
        file_path = sandbox.create_file(filename, app_code)
        if file_path:
            sandbox.open_vscode(file_path)
        
        add_activity_log(f"Generated {framework} web application: {app_name}")
        return f"✅ Created {framework} web application '{app_name}' with endpoints: {endpoints}"
        
    except Exception as e:
        logger.error(f"Error creating web app: {e}")
        return f"Error creating web app: {str(e)}"

@tool
async def create_data_analysis_script(data_file: str = "data.csv", target_column: str = "target") -> str:
    """
    Generate a complete data analysis script with visualizations.
    
    Args:
        data_file: Path to data file
        target_column: Target column for analysis
    
    Example prompts:
    - "Data analysis script बनाओ"
    - "ML data exploration code generate करो"
    """
    try:
        set_jarvis_state(JarvisState.WRITING, "Creating data analysis script...")
        
        analysis_code = _code_generator.generate_code(
            'data_analysis', 'python',
            data_file=data_file,
            target_column=target_column
        )
        
        # Create file in sandbox
        sandbox = get_sandbox()
        filename = f"data_analysis_{target_column}.py"
        file_path = sandbox.create_file(filename, analysis_code)
        
        if file_path:
            sandbox.open_vscode(file_path)
        
        add_activity_log(f"Generated data analysis script for {data_file}")
        return f"✅ Created data analysis script for {data_file} with target column '{target_column}'"
        
    except Exception as e:
        logger.error(f"Error creating data analysis script: {e}")
        return f"Error creating data analysis script: {str(e)}"