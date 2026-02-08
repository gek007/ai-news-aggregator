"""OpenAI news RSS feed scraper."""

import logging
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.scrapers.rss_base import BaseRSSScraper

logger = logging.getLogger(__name__)

OPENAI_NEWS_RSS_URL = "https://openai.com/news/rss.xml"


class OpenAINewsArticle(BaseModel):
    """An article from the OpenAI news RSS feed."""

    title: str
    url: str
    published_at: Optional[datetime] = None
    description: str
    category: Optional[str] = None
    markdown: Optional[str] = None


class OpenAINewsScraper(BaseRSSScraper):
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
        def build_article(entry) -> OpenAINewsArticle:
            return OpenAINewsArticle(
                title=entry.get("title", ""),
                url=entry.get("link", ""),
                published_at=self._parse_published_at(entry),
                description=entry.get("summary", "") or entry.get("description", ""),
                category=self._parse_category(entry),
            )

        return super().parse_rss_feed(rss_url, build_article)

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

        filtered_articles = self._filter_models_by_timeframe(
            articles,
            hours=hours,
            model_cls=OpenAINewsArticle,
        )

        # Fetch markdown content for each article
        for article in filtered_articles:
            try:
                logger.info("Fetching markdown for: %s", article.url)
                article.markdown = self.url_to_markdown(article.url)
            except Exception as e:
                logger.warning("Failed to fetch markdown for %s: %s", article.url, e)

        logger.info(
            "Found %d articles in the last %d hours",
            len(filtered_articles),
            hours,
        )
        return filtered_articles


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
    print(markdown)
