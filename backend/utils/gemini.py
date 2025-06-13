import google.generativeai as genai
import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import asyncio
from functools import partial

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configure Gemini API with API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configure the API with the key
genai.configure(api_key=api_key)

async def run_with_timeout(func, *args, timeout=30, **kwargs):
    """Run a function with a timeout."""
    try:
        return await asyncio.wait_for(asyncio.to_thread(func, *args, **kwargs), timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"Function {func.__name__} timed out after {timeout} seconds")
        raise TimeoutError(f"Operation timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {str(e)}")
        raise

def generate_hook(html_content: str) -> str:
    """Generate a 2-3 sentence hook for an article using Gemini."""
    try:
        # Using gemini-1.5-flash as it's a stable model from the list
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""Given this article content, write a 2-3 sentence hook that captures the most interesting aspects and makes readers want to read more. Focus on the key insights or unique angles.

Article content:
{html_content[:1000]}  # Limit content to first 1000 chars for efficiency

Hook:"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating hook: {str(e)}")
        return ""

def analyze_article(html_content: str, comments: list) -> Dict[str, Any]:
    """Analyze article content and comments using Gemini."""
    try:
        # Using gemini-1.5-flash as it's a stable model from the list
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Limit content and comments for processing
        content = html_content[:2000]  # First 2000 chars of article
        comments_text = "\n".join([f"Comment {i+1}: {c['text'][:200]}" for i, c in enumerate(comments[:5])])  # First 5 comments, 200 chars each
        
        prompt = f"""Analyze this article and its comments. Provide:
1. A brief summary (2-3 sentences)
2. Key points or insights
3. Notable discussion points from comments

Article content:
{content}

Comments:
{comments_text}

Analysis:"""
        
        response = model.generate_content(prompt)
        return {
            "analysis": response.text.strip(),
            "metadata": {
                "model": "gemini-1.5-flash",
                "content_length": len(html_content),
                "comments_analyzed": len(comments)
            }
        }
    except Exception as e:
        logger.error(f"Error analyzing article: {str(e)}")
        return {
            "analysis": "Error analyzing article content.",
            "metadata": {
                "error": str(e),
                "model": "gemini-1.5-flash"
            }
        }

async def generate_hook_async(html_content: str) -> str:
    """Asynchronous wrapper for generate_hook with timeout."""
    return await run_with_timeout(generate_hook, html_content, timeout=30)

async def analyze_article_async(html_content: str, comments: list) -> Dict[str, Any]:
    """Asynchronous wrapper for analyze_article with timeout."""
    return await run_with_timeout(analyze_article, html_content, comments, timeout=60)
