"""
Content extractor module for the RAG ingestion pipeline.
Extracts clean text content from HTML pages while preserving structural information.
"""

import logging
from typing import List, Tuple
from bs4 import BeautifulSoup
from ..models import CrawledPage


logger = logging.getLogger(__name__)


class ContentExtractor:
    """
    Class to extract clean text content from crawled pages while preserving hierarchy.
    """

    def __init__(self):
        """Initialize the content extractor."""
        pass

    def extract_content(self, crawled_page: CrawledPage) -> Tuple[str, List[str]]:
        """
        Extract clean content from a crawled page.

        Args:
            crawled_page: The CrawledPage object to extract content from

        Returns:
            A tuple of (clean content, section hierarchy)
        """
        if not crawled_page.content:
            return "", crawled_page.section_hierarchy

        # Parse the HTML content to clean it further
        soup = BeautifulSoup(crawled_page.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text and clean it up
        text = soup.get_text(separator=' ', strip=True)

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)

        return clean_text, crawled_page.section_hierarchy

    def extract_structured_content(self, crawled_page: CrawledPage) -> List[Tuple[str, str]]:
        """
        Extract content with structural information (headings and their content).

        Args:
            crawled_page: The CrawledPage object to extract structured content from

        Returns:
            A list of tuples containing (heading, content) pairs
        """
        if not crawled_page.content:
            return []

        soup = BeautifulSoup(crawled_page.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract headings and their associated content
        sections = []
        current_heading = "Introduction"  # Default heading if no H1 found
        current_content = []

        # Process all elements in order
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'li', 'pre', 'code']):
            if element.name and element.name.startswith('h') and element.name[1].isdigit():
                # This is a heading
                if current_content:
                    # Save the previous section
                    sections.append((current_heading, ' '.join(current_content).strip()))

                # Set the new heading
                current_heading = element.get_text().strip()
                current_content = []
            else:
                # This is content - add its text to current content
                text = element.get_text().strip()
                if text:
                    current_content.append(text)

        # Don't forget the last section
        if current_content:
            sections.append((current_heading, ' '.join(current_content).strip()))

        return sections

    def extract_content_with_hierarchy(self, crawled_page: CrawledPage) -> str:
        """
        Extract content while preserving the document hierarchy with section markers.

        Args:
            crawled_page: The CrawledPage object to extract hierarchical content from

        Returns:
            Content string with section hierarchy markers
        """
        if not crawled_page.content:
            return ""

        soup = BeautifulSoup(crawled_page.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Build content with hierarchy markers
        content_parts = []

        # Add section hierarchy as context
        if crawled_page.section_hierarchy:
            hierarchy_str = " / ".join(crawled_page.section_hierarchy)
            content_parts.append(f"[SECTION_HIERARCHY: {hierarchy_str}]")

        # Add page title
        if crawled_page.title:
            content_parts.append(f"[PAGE_TITLE: {crawled_page.title}]")

        # Process content with headings
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'li', 'pre', 'code', 'ul', 'ol']):
            if element.name and element.name.startswith('h') and element.name[1].isdigit():
                # This is a heading
                heading_text = element.get_text().strip()
                if heading_text:
                    content_parts.append(f"\n[{element.name.upper()}: {heading_text}]\n")
            else:
                # This is content
                text = element.get_text().strip()
                if text:
                    content_parts.append(text)

        return " ".join(content_parts).strip()


def extract_clean_content(crawled_page: CrawledPage) -> Tuple[str, List[str]]:
    """
    Convenience function to extract clean content from a crawled page.

    Args:
        crawled_page: The CrawledPage object to extract content from

    Returns:
        A tuple of (clean content, section hierarchy)
    """
    extractor = ContentExtractor()
    return extractor.extract_content(crawled_page)


def extract_structured_content(crawled_page: CrawledPage) -> List[Tuple[str, str]]:
    """
    Convenience function to extract structured content from a crawled page.

    Args:
        crawled_page: The CrawledPage object to extract structured content from

    Returns:
        A list of tuples containing (heading, content) pairs
    """
    extractor = ContentExtractor()
    return extractor.extract_structured_content(crawled_page)


def extract_content_with_hierarchy(crawled_page: CrawledPage) -> str:
    """
    Convenience function to extract content with hierarchy markers.

    Args:
        crawled_page: The CrawledPage object to extract hierarchical content from

    Returns:
        Content string with section hierarchy markers
    """
    extractor = ContentExtractor()
    return extractor.extract_content_with_hierarchy(crawled_page)