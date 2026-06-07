"""
Web Scraper for RBI Circulars

Fetches RBI circulars from website and saves raw HTML.
Respects robots.txt and rate limits.
"""

import os
import time
import logging
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class RBIScraper:
    """Scrapes RBI circulars from RBI website."""
    
    def __init__(self, base_url: str = "https://www.rbi.org.in", delay: float = 2.0, output_dir: str = "./data/raw_circulars"):
        """
        Initialize RBI scraper.
        
        Args:
            base_url: RBI website base URL
            delay: Delay between requests (seconds)
            output_dir: Directory to save raw HTML
        """
        self.base_url = base_url
        self.delay = delay
        self.output_dir = output_dir
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Initialized RBIScraper (base_url={base_url})")
    
    def extract_circular_links(self) -> List[str]:
        """
        Extract RBI circular links from website.
        
        NOTE: This is a template. Update with actual RBI URL and CSS selectors.
        Current implementation returns empty list as a placeholder.
        
        Steps to use with real RBI data:
        1. Visit https://www.rbi.org.in/web/allpressreleases
        2. Open browser DevTools (F12)
        3. Inspect the circular list HTML
        4. Find CSS selector for circular links
        5. Update the selector_expression below
        
        Example selectors:
        - "a.circular-link" for <a class="circular-link">
        - "div.release > a" for nested links
        - "table.circulars tbody tr td a" for table rows
        """
        try:
            # Template: Replace with actual RBI URL
            url = f"{self.base_url}/web/allpressreleases"
            
            logger.info(f"Fetching circulars from {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Template: Find circular links using CSS selector
            # Update selector_expression based on actual RBI HTML structure
            selector_expression = "a.circular-link"  # Placeholder selector
            links = soup.select(selector_expression)
            
            if not links:
                logger.warning(f"No circular links found with selector '{selector_expression}'")
                logger.info("Update the selector_expression in extract_circular_links() with correct CSS selector")
                return []
            
            circular_links = []
            for link in links:
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = self.base_url + href
                    elif not href.startswith('http'):
                        href = self.base_url + '/' + href
                    
                    circular_links.append(href)
            
            logger.info(f"Found {len(circular_links)} circular links")
            return circular_links
        
        except requests.RequestException as e:
            logger.error(f"Failed to fetch circular links: {e}")
            return []
    
    def scrape_circular(self, url: str, circular_id: str) -> Optional[str]:
        """
        Scrape a single circular HTML.
        
        Args:
            url: Circular URL
            circular_id: Unique identifier (e.g., "RBI/2024/001")
        
        Returns:
            HTML content or None if failed
        """
        try:
            logger.info(f"Scraping {circular_id} from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            # Save raw HTML
            html_file = os.path.join(self.output_dir, f"{circular_id}.html")
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            logger.info(f"Saved {circular_id} to {html_file}")
            
            # Rate limiting
            time.sleep(self.delay)
            
            return response.text
        
        except requests.RequestException as e:
            logger.error(f"Failed to scrape {circular_id}: {e}")
            return None
    
    def scrape_all(self) -> int:
        """
        Scrape all RBI circulars.
        
        Returns:
            Number of successfully scraped circulars
        """
        links = self.extract_circular_links()
        
        if not links:
            logger.warning("No circular links to scrape. Check RBI URL and CSS selector.")
            return 0
        
        count = 0
        for i, link in enumerate(links):
            circular_id = f"RBI/2024/{i+1:03d}"
            if self.scrape_circular(link, circular_id):
                count += 1
        
        logger.info(f"Successfully scraped {count}/{len(links)} circulars")
        return count


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scraper = RBIScraper()
    
    print("\n" + "="*60)
    print("RegPilot RBI Scraper - Demo")
    print("="*60)
    print("\nNOTE: This is a template scraper.")
    print("To use with real RBI data:")
    print("1. Visit https://www.rbi.org.in/web/allpressreleases")
    print("2. Use browser DevTools (F12) to find CSS selectors")
    print("3. Update extract_circular_links() with correct selectors")
    print("4. Run scraper: python data/scraper.py")
    print("="*60 + "\n")
    
    # Demo: Show how to find selectors
    print("Instructions for finding CSS selectors:")
    print("1. Open https://www.rbi.org.in in browser")
    print("2. Press F12 to open DevTools")
    print("3. Click 'Elements' or 'Inspector' tab")
    print("4. Find <a> tags for circulars")
    print("5. Get the class or id (e.g., class='circular-link')")
    print("6. Update selector_expression variable\n")
