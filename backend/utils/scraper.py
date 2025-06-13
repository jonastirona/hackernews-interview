"""Web scraping utilities for Hacker News and article content.

This module provides functions to:
- Scrape Hacker News frontpage and comments
- Extract and process article content
- Handle bot detection and content validation
"""

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import re
import asyncio
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global browser instance for reuse
_browser = None
_browser_lock = asyncio.Lock()

# Common phrases that indicate bot detection
BOT_DETECTION_PHRASES = [
    "verify you are human",
    "security check",
    "enable javascript",
]

async def get_browser():
    """Get or create a headless browser instance.
    
    Returns:
        Playwright browser instance
    """
    global _browser
    async with _browser_lock:
        if _browser is None:
            playwright = await async_playwright().start()
            _browser = await playwright.chromium.launch(headless=True)
        return _browser

async def close_browser():
    """Close the global browser instance if it exists."""
    global _browser
    async with _browser_lock:
        if _browser is not None:
            try:
                await _browser.close()
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
            finally:
                _browser = None

async def scrape_hn_frontpage(limit=10, offset=0):
    """Scrape stories from Hacker News frontpage.
    
    Args:
        limit: Maximum number of stories to return
        offset: Number of stories to skip
        
    Returns:
        Dictionary containing stories and pagination info
    """
    results = []
    browser = await get_browser()
    page = await browser.new_page()
    try:
        # Handle pagination
        if offset > 0:
            page_num = (offset // 30) + 1  # HN shows 30 stories per page
            await page.goto(f"https://news.ycombinator.com/news?p={page_num}")
        else:
            await page.goto("https://news.ycombinator.com/")

        story_rows = await page.query_selector_all('tr.athing')
        start_idx = offset % 30
        story_rows = story_rows[start_idx:start_idx + limit]
        
        has_more = len(story_rows) > 0
        
        for story_row in story_rows:
            # Extract story data
            title = await story_row.query_selector('.titleline a')
            title_text = await title.inner_text()
            url = await title.get_attribute('href')
            hn_id = await story_row.get_attribute('id')
            
            subtext_row = await page.query_selector(f'tr.athing[id="{hn_id}"] + tr')
            
            # Initialize default values
            points = 0
            author = "unknown"
            comments_count = 0
            
            if subtext_row:
                # Extract points
                score = await subtext_row.query_selector('.score')
                if score:
                    score_text = await score.inner_text()
                    points = int(score_text.split()[0]) if score_text else 0
                
                # Extract author
                user = await subtext_row.query_selector('.hnuser')
                if user:
                    author = await user.inner_text()
                
                # Extract comments count
                links = await subtext_row.query_selector_all('a')
                if links:
                    last_link = links[-1]
                    comments_text = await last_link.inner_text()
                    if "comments" in comments_text:
                        comments_count = int(comments_text.split()[0]) if comments_text else 0
                    elif "discuss" in comments_text:
                        comments_count = 0

            results.append({
                "hn_id": int(hn_id),
                "title": title_text,
                "url": f"https://news.ycombinator.com/item?id={hn_id}",
                "article_url": url, 
                "author": author,
                "points": points,
                "comments_count": comments_count
            })
    finally:
        await page.close()
    return {"stories": results, "has_more": has_more}

def has_bot_detection(text):
    """Check if text contains bot detection phrases.
    
    Args:
        text: Text to check
        
    Returns:
        Trigger phrase if found, None otherwise
    """
    text = text.lower()
    for phrase in BOT_DETECTION_PHRASES:
        if phrase in text:
            return phrase
    return None

async def scrape_full_article(url):
    """Scrape and process article content.
    
    Args:
        url: Article URL to scrape
        
    Returns:
        Dictionary containing article content and metadata
    """
    browser = await get_browser()
    page = await browser.new_page()
    try:
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state('networkidle', timeout=5000)
        
        content = await page.content()
        trigger = has_bot_detection(content)
        if trigger:
            logger.warning(f"Bot detection triggered on {url} by phrase: '{trigger}'")
            return {"error": f"Bot detection triggered by: {trigger}", "html": "<p>Article requires human verification</p>", "text": ""}
        
        html = await page.content()
    except Exception as e:
        logger.error(f"Error loading page {url}: {str(e)}")
        return {"error": f"Error loading page: {str(e)}", "html": "<p>Error loading page</p>", "text": ""}
    finally:
        await page.close()

    try:
        soup = BeautifulSoup(html, "html.parser")
        
        trigger = has_bot_detection(soup.get_text())
        if trigger:
            logger.warning(f"Bot detection triggered in parsed content for {url} by phrase: '{trigger}'")
            return {"error": f"Bot detection triggered by: {trigger}", "html": "<p>Article requires human verification</p>", "text": ""}
        
        # Find main content container
        article = soup.find("main") or soup.find("article")
        
        if not article:
            # Fallback: find largest div with substantial text
            candidates = sorted(
                soup.find_all("div"),
                key=lambda tag: len(tag.get_text(strip=True)),
                reverse=True
            )
            for tag in candidates:
                if len(tag.get_text(strip=True)) > 500:
                    article = tag
                    break
        
        if not article:
            return {"error": "No content found", "html": "", "text": ""}
        
        # Extract metadata
        title = soup.find('title')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        
        metadata = {
            'title': title.text if title else '',
            'description': meta_description.get('content', '') if meta_description else '',
            'og_image': og_image.get('content', '') if og_image else ''
        }
        
        # Process images
        for img in article.find_all('img'):
            src = img.get('src', '')
            if src:
                if not bool(urlparse(src).netloc):
                    src = urljoin(url, src)
                
                img['src'] = src
                if not img.get('alt'):
                    img['alt'] = 'Article image'
                
                img['loading'] = 'lazy'
                img['data-src'] = src
                img['onerror'] = "this.style.display='none'"
        
        # Process videos
        for video in article.find_all('video'):
            src = video.get('src', '')
            if src:
                if not bool(urlparse(src).netloc):
                    src = urljoin(url, src)
                video['src'] = src
                video['onerror'] = "this.style.display='none'"
        
        # Process links
        for a in article.find_all('a'):
            href = a.get('href', '')
            if href and not bool(urlparse(href).netloc):
                a['href'] = urljoin(url, href)
        
        text = article.get_text(separator=" ", strip=True)
        
        return {
            'html': str(article),
            'text': text,
            'metadata': metadata,
            'url': url
        }
    except Exception as e:
        logger.error(f"Error processing content for {url}: {str(e)}")
        return {"error": f"Error processing content: {str(e)}", "html": "<p>Error processing content</p>", "text": ""}

async def scrape_hn_comments(hn_id, offset=0, limit=10):
    """Scrape comments from a Hacker News story.
    
    Args:
        hn_id: Hacker News story ID
        offset: Number of comments to skip
        limit: Maximum number of comments to return
        
    Returns:
        List of comment dictionaries
    """
    browser = await get_browser()
    page = await browser.new_page()
    try:
        await page.goto(f"https://news.ycombinator.com/item?id={hn_id}")
        
        comment_rows = await page.query_selector_all('tr.athing.comtr')
        comment_rows = comment_rows[offset:offset + limit]
        results = []
        
        for row in comment_rows:
            # Extract comment data
            author = await row.query_selector('.hnuser')
            author_text = await author.inner_text() if author else "anonymous"
            
            comment = await row.query_selector('.comment')
            comment_text = await comment.inner_text() if comment else ""
            
            # Calculate comment depth
            indent = await row.query_selector('.ind')
            depth = 0
            if indent:
                img = await indent.query_selector('img')
                if img:
                    width = await img.get_attribute('width')
                    if width:
                        depth = int(width) // 40  # HN uses 40px per level
            
            results.append({
                'author': author_text,
                'text': comment_text,
                'depth': depth
            })
            
        return results
    finally:
        await page.close()