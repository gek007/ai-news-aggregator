"""Anthropic news RSS feed scraper (news, engineering, research feeds combined)."""

import logging
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.scrapers.rss_base import BaseRSSScraper

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


class AnthropicNewsScraper(BaseRSSScraper):
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
        def build_article(entry) -> AnthropicArticle:
            return AnthropicArticle(
                title=entry.get("title", ""),
                url=entry.get("link", ""),
                published_at=self._parse_published_at(entry),
                description=entry.get("summary", "") or entry.get("description", ""),
                category=self._parse_category(entry),
                feed=feed_name,
            )

        return super().parse_rss_feed(rss_url, build_article)

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

        filtered_articles = self._filter_models_by_timeframe(
            all_articles,
            hours=hours,
            model_cls=AnthropicArticle,
        )

        # Fetch markdown content for each article
        for article in filtered_articles:
            try:
                logger.info("Fetching markdown for: %s", article.url)
                article.markdown = self.url_to_markdown(article.url)
            except Exception as e:
                logger.warning("Failed to fetch markdown for %s: %s", article.url, e)

        logger.info(
            "Found %d articles in the last %d hours across %d Anthropic feeds",
            len(filtered_articles),
            hours,
            len(ANTHROPIC_RSS_FEEDS),
        )
        return filtered_articles


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
