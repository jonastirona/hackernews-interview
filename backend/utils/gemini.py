"""Gemini API integration for article analysis and hook generation.

This module provides functions to interact with Google's Gemini API for:
- Generating article hooks
- Analyzing article content and comments
- Content validation and processing
"""

import google.generativeai as genai
import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import asyncio
from functools import partial
import re
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables and configure Gemini API
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=api_key)

# Content validation thresholds
MIN_CONTENT_LENGTH = 50
MAX_CONTENT_LENGTH = 15000
MIN_COMMENT_LENGTH = 5
MAX_COMMENT_LENGTH = 2000
MAX_COMMENTS = 10

def validate_content(content: str, min_length: int = MIN_CONTENT_LENGTH, max_length: int = MAX_CONTENT_LENGTH) -> tuple[bool, str]:
    """Validate and clean content before sending to Gemini.
    
    Args:
        content: The text content to validate
        min_length: Minimum allowed content length
        max_length: Maximum allowed content length
        
    Returns:
        Tuple of (is_valid, cleaned_content)
    """
    if not content or not isinstance(content, str):
        return False, "Content is empty or not a string"
    
    content = re.sub(r'\s+', ' ', content.strip())
    
    if len(content) < min_length:
        return False, f"Content too short (min {min_length} chars)"
    
    if len(content) > max_length:
        content = content[:max_length]
    
    # Check for common error patterns in content
    error_patterns = [
        r'error loading page',
        r'page not found',
        r'404',
        r'403 forbidden',
        r'500 internal server error'
    ]
    
    for pattern in error_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False, f"Content contains error pattern: {pattern}"
    
    return True, content

def validate_comments(comments: list) -> tuple[bool, list]:
    """Validate and clean comments before sending to Gemini.
    
    Args:
        comments: List of comment dictionaries
        
    Returns:
        Tuple of (has_valid_comments, cleaned_comments)
    """
    if not comments or not isinstance(comments, list):
        return False, []
    
    valid_comments = []
    for comment in comments:
        if not isinstance(comment, dict):
            continue
            
        text = comment.get('text', '')
        if not text or not isinstance(text, str):
            continue
            
        is_valid, validated_text = validate_content(
            text,
            min_length=MIN_COMMENT_LENGTH,
            max_length=MAX_COMMENT_LENGTH
        )
        
        if is_valid:
            valid_comments.append({
                'author': comment.get('author', 'anonymous'),
                'text': validated_text,
                'depth': comment.get('depth', 0)
            })
    
    if not valid_comments:
        return False, []
    
    return True, valid_comments[:MAX_COMMENTS]

async def run_with_timeout(func, *args, timeout=30, **kwargs):
    """Run a function with a timeout in an async context.
    
    Args:
        func: Function to run
        timeout: Maximum execution time in seconds
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        Function result
        
    Raises:
        TimeoutError: If function execution exceeds timeout
    """
    try:
        return await asyncio.wait_for(asyncio.to_thread(func, *args, **kwargs), timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"Function {func.__name__} timed out after {timeout} seconds")
        raise TimeoutError(f"Operation timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {str(e)}")
        raise

def generate_hook(html_content: str) -> str:
    """Generate a compelling 2-3 sentence hook for an article.
    
    Args:
        html_content: Article content in HTML or plain text format
        
    Returns:
        Generated hook text or error message
    """
    try:
        # Extract and clean text content from HTML
        if isinstance(html_content, str) and html_content.strip().startswith('<'):
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            content = soup.get_text(separator=' ', strip=True)
            content = ' '.join(content.split())
        else:
            content = html_content

        is_valid, result = validate_content(content)
        if not is_valid:
            logger.warning(f"Invalid content for hook generation: {result}")
            return "Unable to generate a hook for this article. Please click the link to read more."
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Write a compelling 2-3 sentence hook for this technical article. Focus on the most interesting or unique aspects that would make readers want to learn more.

Article content:
{result[:2000]}

Hook:"""
        
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40
            }
        )
        
        hook = response.text.strip()
        if not hook:
            logger.warning("Empty hook generated")
            return "Unable to generate a hook for this article. Please click the link to read more."
            
        if len(hook) > 500:
            hook = hook[:497] + "..."
            
        return hook
        
    except Exception as e:
        logger.error(f"Error generating hook: {str(e)}")
        return "There was an error processing this article. Please click the link to read more."

def analyze_article(html_content: str, comments: list) -> Dict[str, Any]:
    """Analyze article content and comments to generate a structured summary.
    
    Args:
        html_content: Article content in HTML or plain text format
        comments: List of comment dictionaries
        
    Returns:
        Dictionary containing analysis results and metadata
    """
    try:
        # Extract and clean text content from HTML
        if isinstance(html_content, str) and html_content.strip().startswith('<'):
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            content = soup.get_text(separator=' ', strip=True)
            content = ' '.join(content.split())
        else:
            content = html_content

        is_valid, result = validate_content(content)
        if not is_valid:
            logger.warning(f"Invalid content for analysis: {result}")
            return {
                "analysis": "Error: Invalid article content",
                "metadata": {
                    "error": result,
                    "model": "gemini-1.5-flash"
                }
            }
        
        has_valid_comments, valid_comments = validate_comments(comments)
        if not has_valid_comments:
            logger.warning("No valid comments found for analysis")
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        comments_text = ""
        if valid_comments:
            comments_text = "\n".join([
                f"Comment {i+1} by {c['author']}: {c['text'][:300]}"
                for i, c in enumerate(valid_comments)
            ])
        
        prompt = f"""Analyze this technical article and its comments. Structure your response in three clear sections:

1. Summary (2-3 sentences):
2. Key Points:
3. Discussion Highlights:

Article content:
{result[:3000]}

Comments:
{comments_text}

Analysis:"""
        
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40
            }
        )
        
        return {
            "analysis": response.text.strip(),
            "metadata": {
                "model": "gemini-1.5-flash",
                "content_length": len(result),
                "comments_analyzed": len(valid_comments)
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
    """Async wrapper for generate_hook with timeout."""
    return await run_with_timeout(generate_hook, html_content)

async def analyze_article_async(html_content: str, comments: list) -> Dict[str, Any]:
    """Async wrapper for analyze_article with timeout."""
    return await run_with_timeout(analyze_article, html_content, comments)
