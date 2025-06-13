from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import re

async def scrape_hn_frontpage(limit=10):
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://news.ycombinator.com/")

        items = await page.query_selector_all('tr.athing')
        items = items[:limit]
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

        await browser.close()
    return results

async def scrape_full_article(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=30000)
        
        # Wait for images to load
        await page.wait_for_load_state('networkidle')
        
        # Get the full HTML content
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    
    # Try to find the main content container
    main = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r'content|article|post|entry', re.I))
    if not main:
        # Find the div with the most text content
        main = max(soup.find_all("div"), key=lambda d: len(d.get_text()), default=None)
    
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

async def scrape_hn_comments(hn_id, offset=0, limit=10):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
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
            
        await browser.close()
    return results