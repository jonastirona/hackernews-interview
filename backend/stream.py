import json
from .utils.scraper import scrape_hn_frontpage, scrape_full_article, scrape_hn_comments
from .utils.gemini import analyze_article

async def stream_articles(offset=0, limit=10):
    stories = await scrape_hn_frontpage(limit=limit)
    for story in stories:
        yield f"event: log\ndata: Fetching {story['title']}...\n\n"
        
        # Get article content and comments
        article_data = await scrape_full_article(story["article_url"])
        if "error" in article_data:
            yield f"event: error\ndata: {json.dumps({'error': article_data['error'], 'title': story['title']})}\n\n"
            continue
            
        story["full_article_html"] = article_data["html"]
        story["article_metadata"] = article_data["metadata"]
        story["top_comments"] = await scrape_hn_comments(story["hn_id"])
        
        # Analyze with Gemini
        yield f"event: log\ndata: Analyzing {story['title']}...\n\n"
        story["analysis"] = analyze_article(story["full_article_html"], story["top_comments"])
        
        yield f"data: {json.dumps(story)}\n\n"