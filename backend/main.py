from fastapi import FastAPI
from backend.utils.scraper import scrape_hn_frontpage, scrape_full_article, scrape_hn_comments

app = FastAPI()

@app.get("/debug/frontpage")
def test_frontpage():
    return scrape_hn_frontpage()

@app.get("/debug/article")
def test_article(url: str):
    return {"html": scrape_full_article(url)}

@app.get("/debug/comments")
def test_comments(id: int):
    return scrape_hn_comments(id)
