import asyncio
import json
import logging
from utils.scraper import scrape_hn_frontpage, scrape_full_article, scrape_hn_comments
from utils.gemini import generate_hook_async, analyze_article_async
from screenshot import screenshot_manager

logger = logging.getLogger(__name__)

async def stream_articles(offset: int = 0, limit: int = 10):
    """Stream articles with analysis results."""
    try:
        logger.info(f"Starting to stream articles with offset={offset}, limit={limit}")
        
        # Get stories from HN frontpage
        frontpage_data = await scrape_hn_frontpage(limit=limit, offset=offset)
        stories = frontpage_data["stories"]
        logger.info(f"Found {len(stories)} stories")
        
        for story in stories:
            try:
                logger.info(f"Processing story: {story['title']}")
                yield f"event: log\ndata: Fetching {story['title']}...\n\n"
                
                # Get article content and comments
                article_data = await scrape_full_article(story["article_url"])
                if "error" in article_data:
                    error_msg = article_data['error']
                    logger.warning(f"Skipping story '{story['title']}': {error_msg}")
                    yield f"event: log\ndata: Skipping {story['title']}: {error_msg}\n\n"
                    continue
                    
                story["full_article_html"] = article_data["html"]
                story["article_metadata"] = article_data["metadata"]
                
                # Take screenshot of the article
                try:
                    screenshot_path, error = await screenshot_manager.take_screenshot(
                        story["article_url"],
                        story["hn_id"]
                    )
                    if screenshot_path:
                        story["screenshot_path"] = screenshot_path
                        logger.info(f"Successfully took screenshot for story {story['hn_id']}")
                    else:
                        logger.warning(f"Failed to take screenshot for story {story['hn_id']}: {error}")
                        story["screenshot_path"] = None
                except Exception as e:
                    logger.error(f"Error taking screenshot: {str(e)}")
                    story["screenshot_path"] = None
                
                # Generate hook for the article
                try:
                    hook = await generate_hook_async(article_data["html"])
                    if hook:
                        story["hook"] = hook
                        logger.info(f"Generated hook for story {story['hn_id']}")
                    else:
                        logger.warning(f"No hook generated for story {story['hn_id']}")
                        story["hook"] = ""
                except Exception as e:
                    logger.error(f"Error generating hook: {str(e)}")
                    story["hook"] = ""
                
                # Get comments
                try:
                    comments_data = await scrape_hn_comments(story["hn_id"])
                    story["top_comments"] = comments_data["comments"]
                    logger.info(f"Fetched {len(story['top_comments'])} comments for story {story['hn_id']}")
                except Exception as e:
                    logger.error(f"Error fetching comments: {str(e)}")
                    story["top_comments"] = []
                
                # Analyze with Gemini
                yield f"event: log\ndata: Analyzing {story['title']}...\n\n"
                try:
                    analysis_result = await analyze_article_async(story["full_article_html"], story["top_comments"])
                    story["analysis"] = analysis_result
                    logger.info(f"Successfully analyzed article {story['hn_id']}")
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
                data = f"data: {json.dumps(story)}\n\n"
                logger.info(f"Yielding story data: {data[:100]}...")
                yield data
                
                # Add a small delay between stories to prevent overwhelming the client
                await asyncio.sleep(0.1)
                
            except Exception as e:
                error_msg = f"Error processing story {story.get('title', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                yield f"event: error\ndata: {json.dumps({'error': error_msg, 'title': story.get('title', 'unknown')})}\n\n"
                continue  # Continue with next story instead of breaking the stream
        
        # Send complete event after all stories are processed
        yield f"event: complete\ndata: {json.dumps({'has_more': frontpage_data['has_more']})}\n\n"
                
    except Exception as e:
        error_msg = f"Stream error: {str(e)}"
        logger.error(error_msg)
        yield f"event: error\ndata: {json.dumps({'error': error_msg})}\n\n"