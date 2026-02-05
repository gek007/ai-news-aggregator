"""Anthropic news RSS feed scraper (news, engineering, research feeds combined)."""

import feedparser
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional

import trafilatura
from pydantic import BaseModel

from app.scrapers.base import BaseScraper
from app.services.xml_to_markdown import xml_to_markdown as _xml_to_markdown

logger = logging.getLogger(__name__)

ANTHROPIC_RSS_FEEDS = [
    (
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
        "news",
    ),
    (
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
        "engineering",
    ),
    (
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
        "research",
    ),
]


class AnthropicArticle(BaseModel):
    """An article from an Anthropic RSS feed (news, engineering, or research)."""

    title: str
    url: str
    published_at: Optional[datetime] = None
    description: str
    category: Optional[str] = None
    feed: Optional[str] = None  # "news" | "engineering" | "research"
    markdown: Optional[str] = None


class AnthropicNewsScraper(BaseScraper):
    """Scraper for Anthropic content via multiple RSS feeds (news, engineering, research)."""

    def __init__(self):
        super().__init__("Anthropic News")

    def parse_rss_feed(
        self,
        rss_url: str,
        *,
        feed_name: Optional[str] = None,
    ) -> List[AnthropicArticle]:
        """
        Parse a single Anthropic RSS feed and extract article information.

        Args:
            rss_url: URL of the RSS feed.
            feed_name: Optional label for the feed (e.g. "news", "engineering", "research").

        Returns:
            List of AnthropicArticle models.
        """
        try:
            feed = feedparser.parse(rss_url)

            if feed.bozo:
                logger.warning(
                    "Feed parsing issues for %s: %s", rss_url, feed.bozo_exception
                )

            articles: List[AnthropicArticle] = []
            for entry in feed.entries:
                try:
                    published_at = (
                        datetime(*entry.published_parsed[:6])
                        if hasattr(entry, "published_parsed") and entry.published_parsed
                        else None
                    )
                    category = None
                    if hasattr(entry, "tags") and entry.tags:
                        category = entry.tags[0].get("term") or entry.tags[0].get(
                            "label"
                        )
                    article = AnthropicArticle(
                        title=entry.get("title", ""),
                        url=entry.get("link", ""),
                        published_at=published_at,
                        description=entry.get("summary", "")
                        or entry.get("description", ""),
                        category=category,
                        feed=feed_name,
                    )
                    articles.append(article)
                except Exception as e:
                    logger.error("Error parsing Anthropic entry: %s", e)
                    continue

            return articles

        except Exception as e:
            logger.error("Error fetching RSS feed %s: %s", rss_url, e)
            return []

    def fetch_latest(self, hours: int = 24, **kwargs) -> List[AnthropicArticle]:
        """
        Fetch latest articles from all Anthropic feeds (news, engineering, research).

        Args:
            hours: Number of hours to look back (default: 24).

        Returns:
            List of AnthropicArticle models from all feeds, filtered by timeframe.
        """
        all_articles: List[AnthropicArticle] = []

        for rss_url, feed_name in ANTHROPIC_RSS_FEEDS:
            logger.info("Fetching Anthropic feed: %s (%s)", feed_name, rss_url)
            articles = self.parse_rss_feed(rss_url, feed_name=feed_name)
            all_articles.extend(articles)

        dicts = [a.model_dump(mode="python") for a in all_articles]
        filtered_dicts = self.filter_by_timeframe(dicts, hours=hours)
        filtered_articles = [AnthropicArticle(**d) for d in filtered_dicts]

        logger.info(
            "Found %d articles in the last %d hours across %d Anthropic feeds",
            len(filtered_articles),
            hours,
            len(ANTHROPIC_RSS_FEEDS),
        )
        return filtered_articles

    def xml_to_markdown(
        self,
        xml_content: str,
        *,
        root_title: Optional[str] = None,
        max_heading_level: int = 6,
    ) -> str:
        """
        Convert XML string to a human-readable markdown representation.

        Element tags become headings; text nodes become paragraphs.
        Namespace prefixes are stripped from tag names.

        Args:
            xml_content: Raw XML string (e.g. from a file or RSS feed).
            root_title: Optional title for the document (first heading).
            max_heading_level: Maximum markdown heading level 1–6 (default: 6).

        Returns:
            Markdown string representing the XML structure.

        Raises:
            xml.etree.ElementTree.ParseError: If xml_content is not valid XML.
        """
        return _xml_to_markdown(
            xml_content,
            root_title=root_title,
            max_heading_level=max_heading_level,
        )

    def url_to_markdown(
        self,
        url: str,
        *,
        timeout: int = 10,
        root_title: Optional[str] = None,
        max_heading_level: int = 6,
    ) -> str:
        """
        Fetch a URL and convert its content to markdown.

        Uses trafilatura to fetch and extract main content to markdown. If the
        URL returns XML (e.g. RSS), falls back to xml_to_markdown.

        Args:
            url: The URL to fetch (HTML page or RSS/XML feed).
            timeout: Request timeout in seconds (default: 10).
            root_title: Optional title for the markdown document (used for XML fallback).
            max_heading_level: Maximum markdown heading level 1–6 for XML (default: 6).

        Returns:
            The page/feed content as a markdown string.

        Raises:
            ValueError: If the URL could not be fetched.
        """
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise ValueError(f"Could not fetch URL: {url}")
        markdown = trafilatura.extract(downloaded, output_format="markdown")
        if markdown:
            return markdown
        try:
            return self.xml_to_markdown(
                downloaded,
                root_title=root_title,
                max_heading_level=max_heading_level,
            )
        except ET.ParseError:
            return downloaded


if __name__ == "__main__":
    scraper = AnthropicNewsScraper()
    markdown = scraper.url_to_markdown("https://www.anthropic.com/news")
    print(markdown)

    # articles = scraper.fetch_latest(hours=24 * 7)
    # for a in articles[:8]:
    #     print("---")
    #     print("title:", a.title)
    #     print("url:", a.url)
    #     print("published_at:", a.published_at)
    #     print("feed:", a.feed)
    #     print("category:", a.category)
    #     print("description:", (a.description or "")[:120], "...")
