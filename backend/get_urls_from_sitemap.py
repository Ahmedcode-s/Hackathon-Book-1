#!/usr/bin/env python3
"""
Script to extract all URLs from a website's sitemap.xml and save them to a file.
This will be used as input for the RAG ingestion pipeline.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_urls_from_sitemap(website_url: str) -> list:
    """
    Extract all URLs from a website's sitemap.xml

    Args:
        website_url: Base URL of the website

    Returns:
        List of URLs extracted from the sitemap
    """
    sitemap_url = f"{website_url.rstrip('/')}/sitemap.xml"
    print(f"Fetching sitemap from: {sitemap_url}")

    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()

        # Parse the sitemap XML - try xml parser first, fall back to html parser
        try:
            soup = BeautifulSoup(response.content, 'xml')
        except:
            print("XML parser not available, falling back to HTML parser for sitemap")
            soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <url><loc> elements in the sitemap
        loc_elements = soup.find_all('loc')
        urls = [loc.get_text().strip() for loc in loc_elements if loc]

        print(f"Found {len(urls)} URLs in sitemap")

        # If no URLs found, try alternative sitemap patterns
        if not urls:
            print("No URLs found in main sitemap, trying alternatives...")

            alternative_sitemaps = [
                f"{website_url.rstrip('/')}/sitemap_index.xml",
                f"{website_url.rstrip('/')}/sitemap-index.xml",
                f"{website_url.rstrip('/')}/wp-sitemap.xml",  # WordPress
            ]

            for alt_sitemap in alternative_sitemaps:
                try:
                    print(f"Trying alternative sitemap: {alt_sitemap}")
                    alt_response = requests.get(alt_sitemap, timeout=10)
                    alt_response.raise_for_status()

                    # Parse the alternative sitemap
                    try:
                        alt_soup = BeautifulSoup(alt_response.content, 'xml')
                    except:
                        print("XML parser not available, falling back to HTML parser for alternative sitemap")
                        alt_soup = BeautifulSoup(alt_response.content, 'html.parser')

                    alt_loc_elements = alt_soup.find_all('loc')
                    alt_urls = [loc.get_text().strip() for loc in alt_loc_elements if loc]

                    if alt_urls:
                        urls = alt_urls
                        print(f"Found {len(urls)} URLs in alternative sitemap: {alt_sitemap}")
                        break
                except requests.RequestException:
                    continue

        # Filter URLs to only include those from the same domain
        original_domain = urlparse(website_url).netloc
        filtered_urls = []
        for url in urls:
            if urlparse(url).netloc == original_domain:
                filtered_urls.append(url)
            else:
                # If the URL is from the "nine" domain but we're targeting "five",
                # try to convert it to the "five" domain
                parsed_url = urlparse(url)
                if "hackathon-book-1-nine" in parsed_url.netloc and "hackathon-book-1-five" in original_domain:
                    corrected_url = url.replace("hackathon-book-1-nine", "hackathon-book-1-five")
                    print(f"Corrected URL from different domain: {url} -> {corrected_url}")
                    filtered_urls.append(corrected_url)
                else:
                    print(f"Skipping URL from different domain: {url}")

        return filtered_urls

    except requests.RequestException as e:
        print(f"Could not fetch sitemap from {sitemap_url}: {str(e)}")
        return []
    except Exception as e:
        print(f"Error parsing sitemap: {str(e)}")
        return []

def save_urls_to_file(urls: list, filename: str = "sitemap_urls.json"):
    """
    Save the extracted URLs to a file

    Args:
        urls: List of URLs to save
        filename: Name of the file to save to
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(urls, f, indent=2)
    print(f"Saved {len(urls)} URLs to {filename}")

def load_urls_from_file(filename: str = "sitemap_urls.json") -> list:
    """
    Load URLs from a file

    Args:
        filename: Name of the file to load from

    Returns:
        List of URLs
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            urls = json.load(f)
        print(f"Loaded {len(urls)} URLs from {filename}")
        return urls
    except FileNotFoundError:
        print(f"File {filename} not found")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filename}")
        return []

def main():
    # Get website URL from environment variable
    website_url = os.getenv('DEPLOYED_VERCEL_URL')

    if not website_url:
        print("Error: DEPLOYED_VERCEL_URL environment variable not set")
        print("Please set the environment variable with your website URL")
        return

    print(f"Extracting URLs from sitemap for: {website_url}")

    # Extract URLs from sitemap
    urls = extract_urls_from_sitemap(website_url)

    if not urls:
        print("No URLs found in sitemap")
        return

    # Save URLs to file
    save_urls_to_file(urls, "sitemap_urls.json")

    print("\nFirst 10 URLs:")
    for i, url in enumerate(urls[:10]):
        print(f"  {i+1}. {url}")

    if len(urls) > 10:
        print(f"  ... and {len(urls) - 10} more URLs")

if __name__ == "__main__":
    main()