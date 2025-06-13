import asyncio
import json
import logging
import os
from pathlib import Path
from utils.scraper import scrape_hn_frontpage, scrape_full_article, scrape_hn_comments
from utils.gemini import generate_hook_async, analyze_article_async
from screenshot import screenshot_manager

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

def is_valid_story_cache(data):
    # Minimal required fields for a valid cache (must match Story interface)
    required_fields = [
        "hn_id", "title", "url", "article_url", "points", "author", "comments_count", "time",
        "full_article_html", "article_metadata", "screenshot_path", "screenshot_error",
        "hook", "top_comments", "analysis"
    ]
    for field in required_fields:
        if field not in data:
            return False
    return True

async def stream_articles(offset: int = 0, limit: int = 10):
    """Stream articles with analysis results."""
    try:
        logger.info(f"Starting to stream articles with offset={offset}, limit={limit}")
        
        # Get stories from HN frontpage
        frontpage_data = await scrape_hn_frontpage(limit=limit, offset=offset)
        stories = frontpage_data["stories"]
        
        for story in stories:
            try:
                hn_id = str(story.get("id", story.get("hn_id", "")))  # Try both id and hn_id fields
                if not hn_id:
                    logger.error(f"Story missing ID: {story}")
                    continue
                    
                cache_path = os.path.join(CACHE_DIR, f"{hn_id}.json")
                cache_hit = False
                story_data = None
                if os.path.exists(cache_path):
                    try:
                        with open(cache_path, "r", encoding="utf-8") as f:
                            cached = json.load(f)
                        if is_valid_story_cache(cached):
                            cache_hit = True
                            story_data = cached
                        else:
                            logger.warning(f"[CACHE CORRUPT/INCOMPLETE] {hn_id}, reprocessing...")
                    except Exception as e:
                        logger.warning(f"[CACHE ERROR] {hn_id}: {e}, reprocessing...")
                if not cache_hit:
                    try:
                        yield f"event: log\ndata: Fetching {story['title']}...\n\n"
                        
                        # Get article content and comments
                        article_data = await scrape_full_article(story["article_url"])
                        if "error" in article_data:
                            error_msg = article_data['error']
                            logger.warning(f"Could not fetch content for '{story['title']}': {error_msg}")
                            story["full_article_html"] = ""
                            story["article_metadata"] = {}
                        else:
                            story["full_article_html"] = article_data["html"]
                            story["article_metadata"] = article_data["metadata"]
                        
                        # Take screenshot of the article
                        story["screenshot_path"] = None
                        story["screenshot_error"] = None
                        try:
                            screenshot_path, error = await screenshot_manager.take_screenshot(
                                story["article_url"],
                                story["hn_id"]
                            )
                            if screenshot_path:
                                # Ensure screenshot path starts with /static/screenshots/
                                if not screenshot_path.startswith("/static/screenshots/"):
                                    screenshot_path = f"/static/screenshots/{os.path.basename(screenshot_path)}"
                                story["screenshot_path"] = screenshot_path
                            else:
                                story["screenshot_error"] = error
                        except Exception as e:
                            logger.error(f"Error taking screenshot: {str(e)}")
                            story["screenshot_error"] = str(e)
                        
                        # Generate hook for the article
                        try:
                            if story["full_article_html"]:
                                hook = await generate_hook_async(story["full_article_html"])
                                story["hook"] = hook
                            else:
                                story["hook"] = "Unable to fetch article content. Please click the link to read more."
                        except Exception as e:
                            logger.error(f"Error generating hook: {str(e)}")
                            story["hook"] = "There was an error processing this article. Please click the link to read more."
                        
                        # Get comments
                        try:
                            comments_data = await scrape_hn_comments(story["hn_id"])
                            story["top_comments"] = comments_data["comments"]
                        except Exception as e:
                            logger.error(f"Error fetching comments: {str(e)}")
                            story["top_comments"] = []
                        
                        # Analyze with Gemini
                        yield f"event: log\ndata: Analyzing {story['title']}...\n\n"
                        try:
                            if story["full_article_html"]:
                                analysis_result = await analyze_article_async(story["full_article_html"], story["top_comments"])
                                story["analysis"] = analysis_result
                            else:
                                story["analysis"] = {
                                    "analysis": "Content could not be fetched for analysis.",
                                    "metadata": {
                                        "error": "No content available",
                                        "model": "gemini-1.5-flash"
                                    }
                                }
                        except Exception as e:
                            error_msg = f"Error analyzing article: {str(e)}"
                            logger.error(error_msg)
                            story["analysis"] = {
                                "analysis": error_msg,
                                "metadata": {
                                    "error": str(e),
                                    "model": "gemini-1.5-flash"
                                }
                            }
                        
                        # Add has_more flag
                        story["has_more"] = frontpage_data["has_more"]
                        
                        # Yield the story data
                        story_data = {
                            "hn_id": hn_id,
                            "title": story.get("title", ""),
                            "url": story.get("url", ""),
                            "article_url": story.get("article_url", ""),
                            "points": story.get("points", 0),
                            "author": story.get("author", "unknown"),
                            "comments_count": story.get("comments_count", 0),
                            "time": story.get("time", 0),
                            "full_article_html": story.get("full_article_html", ""),
                            "article_metadata": story.get("article_metadata", {}),
                            "screenshot_path": story.get("screenshot_path"),
                            "screenshot_error": story.get("screenshot_error"),
                            "hook": story.get("hook", ""),
                            "top_comments": story.get("top_comments", []),
                            "analysis": story.get("analysis", {}),
                            "has_more": story.get("has_more", False)
                        }
                        # Save to cache
                        try:
                            with open(cache_path, "w", encoding="utf-8") as f:
                                json.dump(story_data, f, ensure_ascii=False)
                        except Exception as e:
                            logger.error(f"[CACHE WRITE ERROR] {hn_id}: {e}")
                        # Ensure screenshot_path is correct for frontend
                        if story_data.get("screenshot_path") and not story_data["screenshot_path"].startswith("/static/"):
                            story_data["screenshot_path"] = "/static/screenshots/" + os.path.basename(story_data["screenshot_path"])
                        yield f"data: {json.dumps(story_data)}\n\n"
                        # Add a small delay between stories to prevent overwhelming the client
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        error_msg = f"Error processing story {story.get('title', 'unknown')}: {str(e)}"
                        logger.error(error_msg)
                        yield f"event: error\ndata: {json.dumps({'error': error_msg, 'title': story.get('title', 'unknown')})}\n\n"
                        continue  # Continue with next story instead of breaking the stream
                else:
                    # For cache hit, ensure screenshot_path is correct for frontend
                    if story_data.get("screenshot_path") and not story_data["screenshot_path"].startswith("/static/"):
                        story_data["screenshot_path"] = "/static/screenshots/" + os.path.basename(story_data["screenshot_path"])
                    yield f"data: {json.dumps(story_data)}\n\n"
            except Exception as e:
                error_msg = f"Error processing story: {str(e)}"
                logger.error(error_msg)
                yield f"event: error\ndata: {json.dumps({'error': error_msg})}\n\n"
        # Send complete event after all stories are processed
        yield f"event: complete\ndata: {json.dumps({'has_more': frontpage_data['has_more']})}\n\n"
                
    except Exception as e:
        error_msg = f"Stream error: {str(e)}"
        logger.error(error_msg)
        yield f"event: error\ndata: {json.dumps({'error': error_msg})}\n\n"