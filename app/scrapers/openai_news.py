"""OpenAI news RSS feed scraper."""

import feedparser
import logging
from datetime import datetime
from typing import List, Optional

import requests
from markdownify import markdownify as md
from pydantic import BaseModel

from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

OPENAI_NEWS_RSS_URL = "https://openai.com/news/rss.xml"

# Browser-like headers to avoid 403 Forbidden from sites that block scrapers
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class OpenAINewsArticle(BaseModel):
    """An article from the OpenAI news RSS feed."""

    title: str
    url: str
    published_at: Optional[datetime] = None
    description: str
    category: Optional[str] = None


class OpenAINewsScraper(BaseScraper):
    """Scraper for OpenAI news via RSS."""

    def __init__(self):
        super().__init__("OpenAI News")

    def parse_rss_feed(
        self, rss_url: str = OPENAI_NEWS_RSS_URL
    ) -> List[OpenAINewsArticle]:
        """
        Parse OpenAI news RSS feed and extract article information.

        Args:
            rss_url: URL of the RSS feed (default: OpenAI news feed).

        Returns:
            List of OpenAINewsArticle models.
        """
        try:
            feed = feedparser.parse(rss_url)

            if feed.bozo:
                logger.warning(
                    "Feed parsing issues for %s: %s", rss_url, feed.bozo_exception
                )

            articles: List[OpenAINewsArticle] = []
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
                    article = OpenAINewsArticle(
                        title=entry.get("title", ""),
                        url=entry.get("link", ""),
                        published_at=published_at,
                        description=entry.get("summary", "")
                        or entry.get("description", ""),
                        category=category,
                    )
                    articles.append(article)
                except Exception as e:
                    logger.error("Error parsing news entry: %s", e)
                    continue

            return articles

        except Exception as e:
            logger.error("Error fetching RSS feed %s: %s", rss_url, e)
            return []

    def fetch_latest(self, hours: int = 24, **kwargs) -> List[OpenAINewsArticle]:
        """
        Fetch latest articles from OpenAI news.

        Args:
            hours: Number of hours to look back (default: 24).

        Returns:
            List of OpenAINewsArticle models filtered by timeframe.
        """
        logger.info("Fetching OpenAI news from %s", OPENAI_NEWS_RSS_URL)
        articles = self.parse_rss_feed(OPENAI_NEWS_RSS_URL)

        dicts = [a.model_dump(mode="python") for a in articles]
        filtered_dicts = self.filter_by_timeframe(dicts, hours=hours)
        filtered_articles = [OpenAINewsArticle(**d) for d in filtered_dicts]

        logger.info(
            "Found %d articles in the last %d hours",
            len(filtered_articles),
            hours,
        )
        return filtered_articles

    def url_to_markdown(
        self,
        url: str,
        *,
        timeout: int = 10,
        **markdownify_options,
    ) -> str:
        """
        Fetch a URL's HTML and convert it to markdown.

        Args:
            url: The URL to fetch.
            timeout: Request timeout in seconds (default: 10).
            **markdownify_options: Optional kwargs passed to markdownify.

        Returns:
            The page content as a markdown string.

        Raises:
            requests.RequestException: On fetch errors.
        """
        response = requests.get(
            url,
            timeout=timeout,
            headers=DEFAULT_HEADERS,
        )
        response.raise_for_status()
        return md(response.text, **markdownify_options)


if __name__ == "__main__":
    scraper = OpenAINewsScraper()
    # articles = scraper.fetch_latest(hours=24 * 7)  # last 7 days for demo
    # for a in articles[:5]:
    #     print("---")
    #     print("title:", a.title)
    #     print("url:", a.url)
    #     print("published_at:", a.published_at)
    #     print("category:", a.category)
    #     print("description:", (a.description or "")[:120], "...")
    markdown = scraper.url_to_markdown("https://openai.com/news/")
    print(md(markdown))
