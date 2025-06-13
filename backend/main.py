from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from utils.scraper import scrape_hn_frontpage, scrape_full_article, scrape_hn_comments, close_browser
from stream import stream_articles
from fastapi.responses import StreamingResponse
from screenshot import screenshot_manager
import os

app = FastAPI()

# Configure CORS
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
    await close_browser()

@app.get("/debug/frontpage")
async def test_frontpage():
    return await scrape_hn_frontpage()

@app.get("/debug/article")
async def test_article(url: str):
    return {"html": await scrape_full_article(url)}

@app.get("/debug/comments")
async def test_comments(id: int, offset: int = 0):
    return await scrape_hn_comments(id, offset=offset)

@app.get("/analyze")
async def analyze(offset: int = 0, limit: int = 10):
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
    """Take a screenshot of the given URL and return the path or error message."""
    screenshot_path, error = await screenshot_manager.take_screenshot(url, article_id)
    if screenshot_path:
        return {"screenshot_path": screenshot_path}
    else:
        return {"error": error or "Failed to take screenshot"}
