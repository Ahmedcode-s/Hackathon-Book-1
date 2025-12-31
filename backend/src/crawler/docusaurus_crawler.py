"""
Docusaurus crawler module for the RAG ingestion pipeline.
Crawls identified URLs from a Docusaurus-based website.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
from typing import List, Dict, Optional
from datetime import datetime
from ..models import CrawledPage
from ..utils.retry_handler import retry_on_exception
from ..utils.id_generator import generate_page_id


logger = logging.getLogger(__name__)


class DocusaurusCrawler:
    """
    Class to crawl Docusaurus-based website pages and extract content.
    """

    def __init__(self, max_concurrent: int = 5):
        """
        Initialize the crawler.

        Args:
            max_concurrent: Maximum number of concurrent requests (default: 5)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RAG-Ingestion-Bot/1.0; +http://example.com/bot)'
        })
        self.max_concurrent = max_concurrent

    @retry_on_exception(max_retries=3, delay=1.0, backoff=2.0)
    def _fetch_page_content(self, url: str) -> str:
        """
        Fetch the content of a single page with retry logic.

        Args:
            url: The URL to fetch

        Returns:
            The HTML content of the page

        Raises:
            requests.RequestException: If the request fails
        """
        response = self.session.get(url, timeout=15)
        response.raise_for_status()
        return response.text

    def _extract_page_title(self, soup: BeautifulSoup) -> str:
        """
        Extract the title from the page.

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            The page title
        """
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()

        # Fallback to h1 if no title tag
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()

        return ""

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract the main content from a Docusaurus page, filtering out navigation elements.

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            The cleaned text content
        """
        # Common Docusaurus content selectors
        content_selectors = [
            'main div[class*="docItemContainer"]',
            'article',
            'main div.container',
            'main div.row',
            '.main-wrapper',
            '.doc-page',
            '.theme-doc-content',
            '[role="main"]',
            'main'
        ]

        content_element = None
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                break

        if not content_element:
            # If no specific content container found, try to remove common navigation elements
            content_element = soup.find('body')

        if content_element:
            # Remove navigation elements that are commonly found in Docusaurus sites
            for element in content_element.find_all(['nav', 'header', 'footer', 'aside']):
                element.decompose()

            # Remove sidebar elements
            for element in content_element.find_all(class_=['sidebar', 'menu', 'nav', 'navigation']):
                element.decompose()

            # Remove header elements
            for element in content_element.find_all(['header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                # Only remove headers if they're likely navigation headers, not content headers
                if element.get('class') and any(cls in element.get('class', []) for cls in ['navbar', 'nav', 'header']):
                    element.decompose()

            # Get the text content
            content = content_element.get_text(separator=' ', strip=True)
            return content

        # Fallback: get all text from body
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)

        return ""

    def _extract_section_hierarchy(self, soup: BeautifulSoup, url: str) -> List[str]:
        """
        Extract the section hierarchy from the page URL and content structure.

        Args:
            soup: BeautifulSoup object of the page
            url: The URL of the page

        Returns:
            A list of section names representing the hierarchy
        """
        # Extract sections from URL path
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        path_parts = [part for part in parsed_url.path.split('/') if part]

        # Common documentation path segments to exclude
        exclude_parts = ['docs', 'doc', 'api', 'guide', 'tutorial']
        sections = [part for part in path_parts if part.lower() not in exclude_parts]

        # Try to find breadcrumbs if available
        breadcrumb_selectors = [
            '.breadcrumbs',
            '.theme-doc-breadcrumb',
            '[aria-label="breadcrumbs"]'
        ]

        for selector in breadcrumb_selectors:
            breadcrumbs = soup.select(selector)
            if breadcrumbs:
                for breadcrumb in breadcrumbs:
                    # Extract text from breadcrumb links
                    links = breadcrumb.find_all('a')
                    breadcrumb_sections = [link.get_text().strip() for link in links if link.get_text().strip()]
                    if breadcrumb_sections:
                        return breadcrumb_sections

        return sections

    def crawl_page(self, url: str) -> Optional[CrawledPage]:
        """
        Crawl a single page and extract its content.

        Args:
            url: The URL to crawl

        Returns:
            A CrawledPage object with the extracted content, or None if crawling failed
        """
        try:
            logger.debug(f"Crawling page: {url}")
            html_content = self._fetch_page_content(url)
            soup = BeautifulSoup(html_content, 'html.parser')

            title = self._extract_page_title(soup)
            content = self._extract_main_content(soup)
            section_hierarchy = self._extract_section_hierarchy(soup, url)

            # Generate a stable page ID
            page_id = generate_page_id(url, title)

            crawled_page = CrawledPage(
                url=url,
                title=title,
                content=content,
                section_hierarchy=section_hierarchy,
                status='success',
                crawled_at=datetime.now(),
                page_id=page_id
            )

            logger.debug(f"Successfully crawled page: {url}")
            return crawled_page

        except Exception as e:
            logger.warning(f"Failed to crawl page {url}: {str(e)}")
            # Return a CrawledPage with error status
            return CrawledPage(
                url=url,
                title="",
                content="",
                section_hierarchy=[],
                status='error',
                crawled_at=datetime.now()
            )

    def crawl_pages(self, urls: List[str]) -> List[CrawledPage]:
        """
        Crawl multiple pages.

        Args:
            urls: List of URLs to crawl

        Returns:
            List of CrawledPage objects
        """
        crawled_pages = []
        failed_count = 0

        logger.info(f"Starting to crawl {len(urls)} pages...")

        for i, url in enumerate(urls):
            logger.info(f"Crawling {i+1}/{len(urls)}: {url}")
            crawled_page = self.crawl_page(url)

            if crawled_page and crawled_page.status == 'success':
                crawled_pages.append(crawled_page)
            else:
                failed_count += 1

        logger.info(f"Crawling completed. Successful: {len(crawled_pages)}, Failed: {failed_count}")
        return crawled_pages


def crawl_docusaurus_pages(urls: List[str]) -> List[CrawledPage]:
    """
    Convenience function to crawl multiple Docusaurus pages.

    Args:
        urls: List of URLs to crawl

    Returns:
        List of CrawledPage objects
    """
    crawler = DocusaurusCrawler()
    return crawler.crawl_pages(urls)