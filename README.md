# 🤖 SachdevaAI Jarvis — Voice-Based AI Assistant

An advanced **voice-based AI assistant** built using **Python**, **LangChain**, and **LiveKit**, designed and developed by **Gaurav Sachdeva**.  
Jarvis interacts with users in **natural Hinglish (Hindi + English)** — just like how modern Indians talk every day — with reasoning capabilities powered by **LangChain Agent Mode**.

---

## 🚀 Overview

**SachdevaAI Jarvis** is not just another chatbot — it’s a thinking assistant.  
It can:
- Understand Hinglish (mix of Hindi and English)
- Speak fluently with personality and humor
- Fetch real-time information (Date, City, Weather)
- Use reasoning and tools via **LangChain Agents**
- Respond naturally through voice using **LiveKit**

This project demonstrates how to connect real-world tools with LLMs to build a contextual, voice-enabled, reasoning assistant.

---

## 🧠 Tech Stack

| Component | Description |
|------------|-------------|
| **Python** | Core programming language used to develop Jarvis |
| **LangChain** | Enables LLM reasoning and tool integration |
| **LiveKit** | Powers real-time voice-based communication |
| **AsyncIO** | Handles asynchronous tasks like API calls |
| **Requests** | Used for fetching user’s city via IP |
| **Custom APIs** | For weather and time fetching |

---

## ⚙️ Features

- 🗣️ **Voice Interaction:** Powered by LiveKit for real-time voice communication  
- 💬 **Hinglish Conversation:** Natural Indian-style responses  
- 🌦️ **Dynamic Context:** Auto-fetches current date, city, and weather  
- 🧩 **Reasoning Mode:** Uses LangChain Agent Mode for tool-based decision-making  
- 🧠 **Personality:** Witty, respectful, and polished assistant tone  
- ⚡ **Asynchronous Execution:** Smooth performance using async functions  

---

## How to get this code:
git clone https://github.com/Gauravsachdeva23e/SachdevaAI_Jarvis_Code.git
cd SachdevaAI_Jarvis_Code


<h1> How to run Jarvis </h1>

## Create a Virtual Environment
python -m venv venv
venv\Scripts\activate          # For Windows

## Install Dependencies
pip install -r requirements.txt

## Run Jarvis
python agent.py console
