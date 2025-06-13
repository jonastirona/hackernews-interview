from fastapi import FastAPI
from .utils.scraper import scrape_hn_frontpage, scrape_full_article, scrape_hn_comments, close_browser
from .stream import stream_articles
from fastapi.responses import StreamingResponse

app = FastAPI()

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
async def test_comments(id: int):
    return await scrape_hn_comments(id)

@app.get("/analyze")
async def analyze(offset: int = 0, limit: int = 10):
    return StreamingResponse(stream_articles(offset, limit), media_type="text/event-stream")
