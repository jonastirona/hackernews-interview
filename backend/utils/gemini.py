import google.generativeai as genai
import logging
import os
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def generate_hook(html_content: str) -> str:
    """Generate a 2-3 sentence hook for an article using Gemini."""
    try:
        model = genai.GenerativeModel('gemini-1.0-flash')
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
        model = genai.GenerativeModel('gemini-1.0-flash')
        
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
                "model": "gemini-1.0-flash",
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
                "model": "gemini-1.0-flash"
            }
        }
