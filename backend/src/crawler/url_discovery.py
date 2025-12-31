"""
URL discovery module for the RAG ingestion pipeline.
Identifies all public URLs from a Docusaurus-based technical book website.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Set
from ..utils.retry_handler import retry_on_exception


logger = logging.getLogger(__name__)


class URLDiscovery:
    """
    Class to discover all public URLs from a Docusaurus-based website.
    """

    def __init__(self, base_url: str, max_depth: int = 3):
        """
        Initialize the URL discovery with the base URL.

        Args:
            base_url: The root URL of the Docusaurus site
            max_depth: Maximum depth to crawl (default: 3)
        """
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RAG-Ingestion-Bot/1.0; +http://example.com/bot)'
        })

    @retry_on_exception(max_retries=3, delay=1.0, backoff=2.0)
    def _fetch_page(self, url: str) -> str:
        """
        Fetch a single page with retry logic.

        Args:
            url: The URL to fetch

        Returns:
            The HTML content of the page

        Raises:
            requests.RequestException: If the request fails
        """
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    def _is_valid_url(self, url: str) -> bool:
        """
        Check if a URL is valid for crawling.

        Args:
            url: The URL to check

        Returns:
            True if the URL is valid for crawling, False otherwise
        """
        parsed = urlparse(url)

        # Check if it's the same domain
        if parsed.netloc != self.base_domain:
            return False

        # Check if it's an HTML page (not a PDF, image, etc.)
        if any(url.lower().endswith(ext) for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.css', '.js']):
            return False

        # Exclude certain patterns
        exclude_patterns = ['/api/', '/assets/', '/static/', '/img/', '/images/']
        if any(pattern in url for pattern in exclude_patterns):
            return False

        return True

    def discover_urls(self) -> List[str]:
        """
        Discover all public URLs from the Docusaurus site.

        Returns:
            A list of discovered URLs
        """
        logger.info(f"Starting URL discovery for: {self.base_url}")

        all_urls: Set[str] = set()
        to_crawl: List[tuple[str, int]] = [(self.base_url, 0)]  # (url, depth)
        crawled: Set[str] = set()

        while to_crawl:
            current_url, depth = to_crawl.pop(0)

            # Skip if already crawled or max depth reached
            if current_url in crawled or depth > self.max_depth:
                continue

            crawled.add(current_url)

            try:
                logger.debug(f"Crawling: {current_url} (depth: {depth})")
                html_content = self._fetch_page(current_url)
                soup = BeautifulSoup(html_content, 'html.parser')

                # Add current URL to the list
                all_urls.add(current_url)

                # Find all links on the page
                links = soup.find_all('a', href=True)

                for link in links:
                    href = link['href']

                    # Convert relative URLs to absolute
                    absolute_url = urljoin(current_url, href)

                    # Check if the URL is valid for crawling
                    if self._is_valid_url(absolute_url) and absolute_url not in crawled:
                        to_crawl.append((absolute_url, depth + 1))

            except Exception as e:
                logger.warning(f"Failed to crawl {current_url}: {str(e)}")
                continue  # Continue with other URLs

        logger.info(f"URL discovery completed. Found {len(all_urls)} URLs.")
        return list(all_urls)


def discover_docusaurus_urls(base_url: str) -> List[str]:
    """
    Convenience function to discover URLs from a Docusaurus site.

    Args:
        base_url: The root URL of the Docusaurus site

    Returns:
        A list of discovered URLs
    """
    discovery = URLDiscovery(base_url)
    return discovery.discover_urls()