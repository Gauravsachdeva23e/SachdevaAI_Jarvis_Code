import os
import requests
import logging
from dotenv import load_dotenv
from datetime import datetime
from langchain.tools import tool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
async def google_search(query: str) -> str:
    """
    Searches Google and returns the top 3 results with heading and summary only.
    No raw links are included to make speech output sound natural.
    
    Args:
        query (str): The search query to look up
        
    Returns:
        str: Formatted search results or error message
    """

    if not query or not query.strip():
        return "Please provide a valid search query."
        
    query = query.strip()
    logger.info(f"Search query received: {query}")

    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        missing = []
        if not api_key:
            missing.append("GOOGLE_SEARCH_API_KEY")
        if not search_engine_id:
            missing.append("SEARCH_ENGINE_ID")
        logger.error(f"Missing environment variables: {missing}")
        return f"Configuration error: Missing environment variables: {', '.join(missing)}"

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "num": 3
    }

    try:
        logger.info("Google Custom Search API को request भेजी जा रही है...")
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return f"Google Search API request failed: {e}"

    if response.status_code != 200:
        logger.error(f"Google API error: {response.status_code} - {response.text}")
        return f"Google Search API में error आया: {response.status_code} - {response.text}"

    data = response.json()
    results = data.get("items", [])

    if not results:
        logger.info("कोई results नहीं मिले।")
        return "कोई results नहीं मिले।"

    # Create a natural, speech-friendly summary
    formatted = "Here are the top results:\n"
    for i, item in enumerate(results, start=1):
        title = item.get("title", "No title")
        snippet = item.get("snippet", "").strip()
        formatted += f"{i}. {title}. {snippet}\n\n"

    return formatted.strip()

@tool
async def get_current_datetime() -> str:
    """
    Returns the current date and time in a human-readable format.

    Use this tool when the user asks for the current time, date, or wants to know what day it is.
    Example prompts:
    - "अब क्या time हो रहा है?"
    - "आज की तारीख क्या है?"
    - "What’s the time right now?"
    """

    now = datetime.now()
    formatted = now.strftime("%d %B %Y, %I:%M %p")  # Example: 31 July 2025, 04:22 PM
    return formatted