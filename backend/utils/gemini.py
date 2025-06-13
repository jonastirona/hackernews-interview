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

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configure Gemini API with API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configure the API with the key
genai.configure(api_key=api_key)

# Content validation constants
MIN_CONTENT_LENGTH = 50
MAX_CONTENT_LENGTH = 15000
MIN_COMMENT_LENGTH = 5
MAX_COMMENT_LENGTH = 2000
MAX_COMMENTS = 10

def validate_content(content: str, min_length: int = MIN_CONTENT_LENGTH, max_length: int = MAX_CONTENT_LENGTH) -> tuple[bool, str]:
    """Validate content before sending to Gemini."""
    if not content or not isinstance(content, str):
        return False, "Content is empty or not a string"
    
    # Remove extra whitespace
    content = re.sub(r'\s+', ' ', content.strip())
    
    if len(content) < min_length:
        return False, f"Content too short (min {min_length} chars)"
    
    if len(content) > max_length:
        # Instead of failing, truncate the content
        content = content[:max_length]
    
    # Only check for critical error patterns
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
    """Validate comments before sending to Gemini."""
    if not comments or not isinstance(comments, list):
        return False, []
    
    valid_comments = []
    for comment in comments:
        if not isinstance(comment, dict):
            continue
            
        text = comment.get('text', '')
        if not text or not isinstance(text, str):
            continue
            
        # Validate comment text with more lenient settings
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
    
    # Limit number of comments
    valid_comments = valid_comments[:MAX_COMMENTS]
    return True, valid_comments

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
        # Extract text content from HTML if needed
        if isinstance(html_content, str) and html_content.strip().startswith('<'):
            soup = BeautifulSoup(html_content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            # Get text and clean it
            content = soup.get_text(separator=' ', strip=True)
            # Remove extra whitespace and normalize
            content = ' '.join(content.split())
        else:
            content = html_content

        # Validate content
        is_valid, result = validate_content(content)
        if not is_valid:
            logger.warning(f"Invalid content for hook generation: {result}")
            return ""
        
        # # Using gemini-1.5-flash as it's a stable model from the list
        # model = genai.GenerativeModel('gemini-1.5-flash')
        
        # # Create a more focused prompt
        # prompt = f"""Write a compelling 2-3 sentence hook for this technical article. Focus on the most interesting or unique aspects that would make readers want to learn more.

        # Article content:
        # {result[:2000]}

        # Hook:"""
        
        # # Generate with minimal safety settings
        # response = model.generate_content(
        #     prompt,
        #     generation_config={
        #         "temperature": 0.7,
        #         "top_p": 0.8,
        #         "top_k": 40
        #     }
        # )
        
        # # Extract and clean the response
        # hook = response.text.strip()
        # if not hook:
        #     logger.warning("Empty hook generated")
        #     return ""
            
        # # Ensure the hook is not too long
        # if len(hook) > 500:
        #     hook = hook[:497] + "..."
            
        # return hook
        
        # Return placeholder instead of making API call
        return "This is a placeholder hook for the article. The actual hook generation is temporarily disabled to save API requests."
        
    except Exception as e:
        logger.error(f"Error generating hook: {str(e)}")
        return ""

def analyze_article(html_content: str, comments: list) -> Dict[str, Any]:
    """Analyze article content and comments using Gemini."""
    try:
        # Extract text content from HTML if needed
        if isinstance(html_content, str) and html_content.strip().startswith('<'):
            soup = BeautifulSoup(html_content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            # Get text and clean it
            content = soup.get_text(separator=' ', strip=True)
            # Remove extra whitespace and normalize
            content = ' '.join(content.split())
        else:
            content = html_content

        # Validate content
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
        
        # Validate comments
        has_valid_comments, valid_comments = validate_comments(comments)
        if not has_valid_comments:
            logger.warning("No valid comments found for analysis")
        
        # # Using gemini-1.5-flash as it's a stable model from the list
        # model = genai.GenerativeModel('gemini-1.5-flash')
        
        # # Format comments
        # comments_text = ""
        # if valid_comments:
        #     comments_text = "\n".join([
        #         f"Comment {i+1} by {c['author']}: {c['text'][:300]}"
        #         for i, c in enumerate(valid_comments)
        #     ])
        
        # # Create a more structured prompt
        # prompt = f"""Analyze this technical article and its comments. Structure your response in three clear sections:

        # 1. Summary (2-3 sentences):
        # 2. Key Points:
        # 3. Discussion Highlights:

        # Article content:
        # {result[:3000]}

        # Comments:
        # {comments_text}

        # Analysis:"""
        
        # # Generate with minimal safety settings
        # response = model.generate_content(
        #     prompt,
        #     generation_config={
        #         "temperature": 0.7,
        #         "top_p": 0.8,
        #         "top_k": 40
        #     }
        # )
        
        # return {
        #     "analysis": response.text.strip(),
        #     "metadata": {
        #         "model": "gemini-1.5-flash",
        #         "content_length": len(result),
        #         "comments_analyzed": len(valid_comments)
        #     }
        # }

        # Return placeholder instead of making API call
        return {
            "analysis": """This is a placeholder analysis for the article. The actual analysis is temporarily disabled to save API requests.

1. Summary (2-3 sentences):
This is a placeholder summary.

2. Key Points:
- Placeholder key point 1
- Placeholder key point 2
- Placeholder key point 3

3. Discussion Highlights:
- Placeholder discussion point 1
- Placeholder discussion point 2""",
            "metadata": {
                "model": "gemini-1.5-flash",
                "content_length": len(result),
                "comments_analyzed": len(valid_comments),
                "placeholder": True
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
    """Async wrapper for generate_hook."""
    return await run_with_timeout(generate_hook, html_content)

async def analyze_article_async(html_content: str, comments: list) -> Dict[str, Any]:
    """Async wrapper for analyze_article."""
    return await run_with_timeout(analyze_article, html_content, comments)
