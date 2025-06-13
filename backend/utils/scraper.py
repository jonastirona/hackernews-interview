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

        # Get all story rows
        story_rows = await page.query_selector_all('tr.athing')
        start_idx = offset % 30
        story_rows = story_rows[start_idx:start_idx + limit]
        
        # Check if we've reached the end
        has_more = len(story_rows) > 0
        
        for story_row in story_rows:
            # Get the story data
            title = await story_row.query_selector('.titleline a')
            title_text = await title.inner_text()
            url = await title.get_attribute('href')
            hn_id = await story_row.get_attribute('id')
            
            # Get the subtext row that follows this story row
            subtext_row = await page.query_selector(f'tr.athing[id="{hn_id}"] + tr')
            
            # Initialize default values
            points = 0
            author = "unknown"
            comments_count = 0
            
            if subtext_row:
                # Get points
                score = await subtext_row.query_selector('.score')
                if score:
                    score_text = await score.inner_text()
                    points = int(score_text.split()[0]) if score_text else 0
                
                # Get author
                user = await subtext_row.query_selector('.hnuser')
                if user:
                    author = await user.inner_text()
                
                # Get comments count - look for the last link in the subtext row
                links = await subtext_row.query_selector_all('a')
                if links:
                    last_link = links[-1]  # The comments link is always the last one
                    comments_text = await last_link.inner_text()
                    if "comments" in comments_text:
                        comments_count = int(comments_text.split()[0]) if comments_text else 0
                    elif "discuss" in comments_text:
                        comments_count = 0

            results.append({
                "hn_id": int(hn_id),
                "title": title_text,
                "url": f"https://news.ycombinator.com/item?id={hn_id}",  # Link to HN discussion
                "article_url": url,  # Link to actual article
                "author": author,
                "points": points,
                "comments_count": comments_count
            })
    finally:
        await page.close()
    return {"stories": results, "has_more": has_more}

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
            return {"error": f"Bot detection triggered by: {trigger}", "html": "<p>Article requires human verification</p>", "text": ""}
        
        # Get the full HTML content
        html = await page.content()
    except Exception as e:
        logger.error(f"Error loading page {url}: {str(e)}")
        return {"error": f"Error loading page: {str(e)}", "html": "<p>Error loading page</p>", "text": ""}
    finally:
        await page.close()

    try:
        soup = BeautifulSoup(html, "html.parser")
        
        # Check for bot detection in the parsed content
        trigger = has_bot_detection(soup.get_text())
        if trigger:
            logger.warning(f"Bot detection triggered in parsed content for {url} by phrase: '{trigger}'")
            return {"error": f"Bot detection triggered by: {trigger}", "html": "<p>Article requires human verification</p>", "text": ""}
        
        # Try to find the main content container
        article = soup.find("main") or soup.find("article")
        
        if not article:
            # Fallback: largest div with text length > 500
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
        
        # Get metadata
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
                
                # Add error handling for images
                img['onerror'] = "this.style.display='none'"
        
        # Process videos
        for video in article.find_all('video'):
            # Get video source
            src = video.get('src', '')
            if src:
                # Convert relative URLs to absolute
                if not bool(urlparse(src).netloc):
                    src = urljoin(url, src)
                video['src'] = src
                
                # Add error handling for videos
                video['onerror'] = "this.style.display='none'"
        
        # Process links to make them absolute
        for a in article.find_all('a'):
            href = a.get('href', '')
            if href and not bool(urlparse(href).netloc):
                a['href'] = urljoin(url, href)
        
        # Get clean text
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
    browser = await get_browser()
    page = await browser.new_page()
    try:
        await page.goto(f"https://news.ycombinator.com/item?id={hn_id}")
        
        # Get all comment rows (each comment is in a tr.athing followed by tr)
        comment_rows = await page.query_selector_all('tr.athing.comtr')
        # Apply pagination
        comment_rows = comment_rows[offset:offset + limit]
        results = []
        
        # Check if we've reached the end
        has_more = len(comment_rows) > 0
        
        for comment_row in comment_rows:
            # Get the comment ID
            comment_id = await comment_row.get_attribute('id')
            # Get the comment container (the tr after the athing)
            comment_container = await page.query_selector(f'tr.athing[id="{comment_id}"] + tr')
            if not comment_container:
                continue
                
            # Get the comment text container
            comment_text_container = await comment_container.query_selector('.commtext')
            if not comment_text_container:
                continue
                
            # Get the username from the .hnuser link
            user_link = await comment_container.query_selector('a.hnuser')
            user_text = "anonymous"
            if user_link:
                try:
                    user_text = await user_link.inner_text()
                    user_text = user_text.strip()
                except Exception as e:
                    logger.warning(f"Error extracting username: {str(e)}")
            
            # Get the comment text
            text = ""
            try:
                text = await comment_text_container.inner_text()
                text = text.strip()
            except Exception as e:
                logger.warning(f"Error extracting comment text: {str(e)}")
            
            # Get the comment depth
            depth = 0
            try:
                indent_img = await comment_row.query_selector('td.ind img')
                if indent_img:
                    width = await indent_img.get_attribute('width')
                    if width:
                        depth = int(width) // 40
            except Exception as e:
                logger.warning(f"Error extracting comment depth: {str(e)}")
            
            results.append({
                "author": user_text,
                "text": text,
                "depth": depth
            })
    except Exception as e:
        logger.error(f"Error scraping comments for story {hn_id}: {str(e)}")
        return {"comments": [], "has_more": False}
    finally:
        await page.close()
    return {"comments": results, "has_more": has_more}