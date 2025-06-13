"""FastAPI application for Hacker News article analysis.

This module sets up the FastAPI application with:
- CORS middleware for frontend communication
- Static file serving for screenshots
- API endpoints for article analysis and debugging
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from utils.scraper import scrape_hn_frontpage, scrape_full_article, scrape_hn_comments, close_browser
from stream import stream_articles
from fastapi.responses import StreamingResponse
from screenshot import screenshot_manager
import os

app = FastAPI(
    title="Hacker News Article Analysis",
    description="API for analyzing Hacker News articles with AI-generated summaries and screenshots",
    version="1.0.0"
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mount static files directory for screenshots
screenshots_dir = os.path.join(os.path.dirname(__file__), "static/screenshots")
os.makedirs(screenshots_dir, exist_ok=True)
app.mount("/static/screenshots", StaticFiles(directory=screenshots_dir), name="screenshots")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up browser resources on application shutdown."""
    await close_browser()

@app.get("/debug/frontpage")
async def test_frontpage():
    """Debug endpoint to test Hacker News frontpage scraping."""
    return await scrape_hn_frontpage()

@app.get("/debug/article")
async def test_article(url: str):
    """Debug endpoint to test article content scraping.
    
    Args:
        url: URL of the article to scrape
    """
    return {"html": await scrape_full_article(url)}

@app.get("/debug/comments")
async def test_comments(id: int, offset: int = 0):
    """Debug endpoint to test comment scraping.
    
    Args:
        id: Hacker News story ID
        offset: Number of comments to skip
    """
    return await scrape_hn_comments(id, offset=offset)

@app.get("/analyze")
async def analyze(offset: int = 0, limit: int = 10):
    """Stream articles with AI analysis results.
    
    Args:
        offset: Number of stories to skip
        limit: Maximum number of stories to process
        
    Returns:
        Server-sent events stream with article data and analysis
    """
    return StreamingResponse(
        stream_articles(offset, limit),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"  # Add CORS header for SSE
        }
    )

@app.get("/screenshot/{article_id}")
async def take_screenshot(article_id: str, url: str):
    """Take a screenshot of an article.
    
    Args:
        article_id: Unique identifier for the article
        url: URL of the article to screenshot
        
    Returns:
        Dictionary containing screenshot path or error message
    """
    screenshot_path, error = await screenshot_manager.take_screenshot(url, article_id)
    if screenshot_path:
        return {"screenshot_path": screenshot_path}
    else:
        return {"error": error or "Failed to take screenshot"}
