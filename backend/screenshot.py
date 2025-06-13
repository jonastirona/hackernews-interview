from playwright.async_api import async_playwright, TimeoutError
import asyncio
import os
from pathlib import Path
from typing import Optional, Tuple
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Update paths to be relative to the backend directory
FALLBACK_IMAGE = os.path.join(os.path.dirname(__file__), "static/screenshots/fallback.png")

class ScreenshotManager:
    def __init__(self, screenshot_dir: str = None):
        if screenshot_dir is None:
            screenshot_dir = os.path.join(os.path.dirname(__file__), "static/screenshots")
        self.screenshot_dir = screenshot_dir
        # Create screenshot directory if it doesn't exist
        Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
        # Ensure fallback image exists (create a simple one if not)
        if not os.path.exists(FALLBACK_IMAGE):
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (1280, 800), color=(240, 240, 240))
            d = ImageDraw.Draw(img)
            d.text((100, 350), "Screenshot unavailable", fill=(0, 0, 0))
            img.save(FALLBACK_IMAGE)

    async def take_screenshot(self, url: str, article_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Take a screenshot of the given URL and save it to the screenshot directory.
        Returns (path, message): path to the saved screenshot or None, and a message if blocked/failed.
        """
        # Check if screenshot already exists
        filename = f"{article_id}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        if os.path.exists(filepath):
            logger.info(f"Screenshot already exists for article {article_id}, returning existing file")
            return f"/static/screenshots/{filename}", None

        browser = None
        context = None
        page = None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-software-rasterizer",
                    "--disable-extensions"
                ])
                
                # Enhanced browser context with more realistic settings
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="en-US",
                    timezone_id="America/New_York",
                    viewport={'width': 1280, 'height': 800},
                    device_scale_factor=1,
                    has_touch=False,
                    is_mobile=False,
                    color_scheme="light",
                    accept_downloads=True,
                    extra_http_headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "DNT": "1",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-User": "?1",
                        "Cache-Control": "max-age=0"
                    }
                )
                
                page = await context.new_page()

                # Enhanced anti-detection measures
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                    window.chrome = { runtime: {} };
                """)

                # Random delay to mimic human behavior
                await asyncio.sleep(random.uniform(1.0, 2.5))

                try:
                    # Set a longer timeout for loading pages
                    response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    if not response:
                        return None, "Failed to load page: No response"
                    
                    # Simulate human-like scrolling
                    await page.evaluate("""
                        window.scrollTo({
                            top: Math.floor(Math.random() * 100),
                            behavior: 'smooth'
                        });
                    """)
                    await asyncio.sleep(random.uniform(0.5, 1.0))
                    
                    # Wait for network to be idle
                    try:
                        await page.wait_for_load_state("networkidle", timeout=30000)
                    except TimeoutError:
                        logger.warning("Network did not become idle, continuing anyway")
                    
                    # Additional wait for dynamic content
                    await asyncio.sleep(2)
                    
                    # Check if page is still valid
                    if page.is_closed():
                        return None, "Page was closed unexpectedly"

                    # Enhanced block detection
                    content = await page.content()
                    block_phrases = [
                        "blocked", "robot", "suspect", "unusual traffic", "verify you are a human",
                        "security check", "captcha", "wordpress", "wp-content", "wp-includes"
                    ]
                    
                    # Check for WordPress-specific elements
                    is_wordpress = await page.evaluate("""
                        () => {
                            return document.querySelector('meta[name="generator"][content*="WordPress"]') !== null ||
                                   document.querySelector('link[href*="wp-content"]') !== null ||
                                   document.querySelector('script[src*="wp-includes"]') !== null;
                        }
                    """)
                    
                    if is_wordpress:
                        # Additional wait for WordPress content
                        await asyncio.sleep(3)
                        # Try to scroll more to load lazy content
                        await page.evaluate("""
                            window.scrollTo({
                                top: document.body.scrollHeight / 2,
                                behavior: 'smooth'
                            });
                        """)
                        await asyncio.sleep(2)

                    if any(phrase in content.lower() for phrase in block_phrases):
                        logger.warning(f"Blocked or bot detected at {url}, returning block message.")
                        return None, "Screenshot blocked by site"

                    # Try to take screenshot with different viewport sizes if needed
                    for viewport_height in [800, 1200, 1600]:
                        try:
                            if page.is_closed():
                                return None, "Page was closed during screenshot attempt"
                                
                            await page.set_viewport_size({'width': 1280, 'height': viewport_height})
                            await asyncio.sleep(1)  # Wait for resize
                            
                            # Additional check for page validity
                            if not page.is_closed():
                                await page.screenshot(path=filepath, full_page=True)
                                break
                            else:
                                return None, "Page was closed during screenshot attempt"
                                
                        except Exception as e:
                            logger.warning(f"Failed to take screenshot with height {viewport_height}: {str(e)}")
                            if viewport_height == 1600:  # Last attempt
                                raise
                            continue

                    return f"/static/screenshots/{filename}", None

                except TimeoutError:
                    logger.error(f"Timeout while loading {url}")
                    return None, "Timeout while loading page"
                except Exception as e:
                    logger.error(f"Error during page interaction: {str(e)}")
                    return None, f"Error during page interaction: {str(e)}"

        except Exception as e:
            logger.error(f"Failed to take screenshot of {url}: {str(e)}")
            return None, f"Failed to take screenshot: {str(e)}"
        finally:
            if page and not page.is_closed():
                try:
                    await page.close()
                except Exception as e:
                    logger.error(f"Error closing page: {str(e)}")
            if context:
                try:
                    await context.close()
                except Exception as e:
                    logger.error(f"Error closing context: {str(e)}")
            if browser:
                try:
                    await browser.close()
                except Exception as e:
                    logger.error(f"Error closing browser: {str(e)}")

# Create a singleton instance
screenshot_manager = ScreenshotManager() 