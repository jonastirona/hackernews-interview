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

# Global browser instance
_browser = None
_browser_lock = asyncio.Lock()

# Common bot detection phrases
BOT_DETECTION_PHRASES = [
    "verify you are human",
    "security check",
    "enable javascript",
]

async def get_browser():
    global _browser
    async with _browser_lock:
        if _browser is None:
            playwright = await async_playwright().start()
            _browser = await playwright.chromium.launch(headless=True)
        return _browser

async def close_browser():
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
    results = []
    browser = await get_browser()
    page = await browser.new_page()
    try:
        # If offset is greater than 0, we need to go to the next page
        if offset > 0:
            page_num = (offset // 30) + 1  # HN shows 30 stories per page
            await page.goto(f"https://news.ycombinator.com/news?p={page_num}")
        else:
            await page.goto("https://news.ycombinator.com/")

        items = await page.query_selector_all('tr.athing')
        # Calculate the correct slice based on offset
        start_idx = offset % 30
        items = items[start_idx:start_idx + limit]
        
        for item in items:
            title = await item.query_selector('.titleline a')
            title_text = await title.inner_text()
            url = await title.get_attribute('href')
            hn_id = await item.get_attribute('id')
            # Get the subtext row which follows the athing row
            subtext = await page.query_selector(f'tr:has(td.subtext) + tr[data-hnid="{hn_id}"]')
            points = "0 points"
            author = "unknown"
            if subtext:
                score = await subtext.query_selector('.score')
                if score:
                    points = await score.inner_text()
                user = await subtext.query_selector('.hnuser')
                if user:
                    author = await user.inner_text()

            results.append({
                "hn_id": int(hn_id),
                "title": title_text,
                "article_url": url,
                "author": author,
                "points": points
            })
    finally:
        await page.close()
    return results

def has_bot_detection(text):
    """Check if the text contains bot detection phrases and return the trigger if found."""
    text = text.lower()
    for phrase in BOT_DETECTION_PHRASES:
        if phrase in text:
            return phrase
    return None

async def scrape_full_article(url):
    browser = await get_browser()
    page = await browser.new_page()
    try:
        # Set a longer timeout for loading pages
        await page.goto(url, timeout=30000)
        
        # Wait for content to load
        await page.wait_for_load_state('networkidle', timeout=5000)
        
        # Check for bot detection
        content = await page.content()
        trigger = has_bot_detection(content)
        if trigger:
            logger.warning(f"Bot detection triggered on {url} by phrase: '{trigger}'")
            return {"error": f"Bot detection triggered by: {trigger}", "html": "<p>Article requires human verification</p>"}
        
        # Get the full HTML content
        html = await page.content()
    except Exception as e:
        logger.error(f"Error loading page {url}: {str(e)}")
        return {"error": f"Error loading page: {str(e)}", "html": "<p>Error loading page</p>"}
    finally:
        await page.close()

    try:
        soup = BeautifulSoup(html, "html.parser")
        
        # Check for bot detection in the parsed content
        trigger = has_bot_detection(soup.get_text())
        if trigger:
            logger.warning(f"Bot detection triggered in parsed content for {url} by phrase: '{trigger}'")
            return {"error": f"Bot detection triggered by: {trigger}", "html": "<p>Article requires human verification</p>"}
        
        # Try to find the main content container
        main = None
        
        # Try common article content selectors
        selectors = [
            "main",
            "article",
            "div.content",
            "div.article",
            "div.post",
            "div.entry-content",
            "div.post-content",
            "div#content",
            "div.container",
            "div.wrapper"
        ]
        
        for selector in selectors:
            main = soup.select_one(selector)
            if main and len(main.get_text().strip()) > 100:  # Ensure we have substantial content
                break
        
        # If no specific content found, try to find the div with the most text content
        if not main:
            divs = soup.find_all("div")
            if divs:
                main = max(divs, key=lambda d: len(d.get_text().strip()))
        
        # If still no content, use the body
        if not main or len(main.get_text().strip()) < 100:
            main = soup.find("body")
        
        if not main:
            return {"error": "Could not extract content", "html": "<p>Could not extract content</p>"}
        
        # Process images
        for img in main.find_all('img'):
            # Get image source
            src = img.get('src', '')
            if src:
                # Convert relative URLs to absolute
                if not bool(urlparse(src).netloc):
                    src = urljoin(url, src)
                
                # Get image dimensions and alt text
                img['src'] = src
                if not img.get('alt'):
                    img['alt'] = 'Article image'
                
                # Add loading="lazy" for better performance
                img['loading'] = 'lazy'
                
                # Add data-src for lazy loading
                img['data-src'] = src
        
        # Process links to make them absolute
        for a in main.find_all('a'):
            href = a.get('href', '')
            if href and not bool(urlparse(href).netloc):
                a['href'] = urljoin(url, href)
        
        # Get metadata
        title = soup.find('title')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        
        metadata = {
            'title': title.text if title else '',
            'description': meta_description.get('content', '') if meta_description else '',
            'og_image': og_image.get('content', '') if og_image else ''
        }
        
        return {
            'html': str(main),
            'metadata': metadata,
            'url': url
        }
    except Exception as e:
        logger.error(f"Error processing content for {url}: {str(e)}")
        return {"error": f"Error processing content: {str(e)}", "html": "<p>Error processing content</p>"}

async def scrape_hn_comments(hn_id, offset=0, limit=10):
    browser = await get_browser()
    page = await browser.new_page()
    try:
        await page.goto(f"https://news.ycombinator.com/item?id={hn_id}")
        
        comments = await page.query_selector_all('.commtext')
        comments = comments[:limit]
        results = []
        
        for comment in comments:
            user = await comment.evaluate('(element) => element.closest(".comment").querySelector(".hnuser")?.textContent || "anonymous"')
            text = await comment.inner_text()
            results.append({
                "user": user,
                "comment": text
            })
    finally:
        await page.close()
    return results