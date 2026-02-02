"""Kick-off aggregation: fetch latest from YouTube, Anthropic, and OpenAI and persist to DB."""

import logging
from typing import Any, List

from app.config import YOUTUBE_CHANNEL_IDS
from app.database import get_session, Repository
from app.scrapers.anthropic_news import AnthropicNewsScraper
from app.scrapers.openai_news import OpenAINewsScraper
from app.scrapers.youtube_rss import YouTubeRSSScraper

logger = logging.getLogger(__name__)


def run(hours: int = 24, persist: bool = True) -> dict[str, List[Any]]:
    """
    Fetch newest content from all sources (last N hours) and optionally persist to DB.

    - YouTube: channels from app.config.YOUTUBE_CHANNEL_IDS
    - Anthropic: fixed news/engineering/research feeds
    - OpenAI: fixed news RSS feed

    Args:
        hours: How far back to look (default: 24).
        persist: If True (default), save all items to the database via Repository.

    Returns:
        Dict with keys "youtube", "anthropic", "openai", each a list of items from this run.
    """
    result: dict[str, List[Any]] = {
        "youtube": [],
        "anthropic": [],
        "openai": [],
    }

    if YOUTUBE_CHANNEL_IDS:
        youtube = YouTubeRSSScraper()
        result["youtube"] = youtube.fetch_latest(YOUTUBE_CHANNEL_IDS, hours=hours)
        logger.info("YouTube: %d new items in this run", len(result["youtube"]))
    else:
        logger.info("YouTube: no channels configured, skipping")

    anthropic = AnthropicNewsScraper()
    result["anthropic"] = anthropic.fetch_latest(hours=hours)
    logger.info("Anthropic: %d new items in this run", len(result["anthropic"]))

    openai_scraper = OpenAINewsScraper()
    result["openai"] = openai_scraper.fetch_latest(hours=hours)
    logger.info("OpenAI: %d new items in this run", len(result["openai"]))

    if persist and (result["youtube"] or result["anthropic"] or result["openai"]):
        session = get_session()
        try:
            repo = Repository(session)
            if result["youtube"]:
                n = repo.add_youtube_videos(result["youtube"])
                logger.info("Persisted %d YouTube videos", n)
            if result["anthropic"]:
                n = repo.add_anthropic_articles(result["anthropic"])
                logger.info("Persisted %d Anthropic articles", n)
            if result["openai"]:
                n = repo.add_openai_articles(result["openai"])
                logger.info("Persisted %d OpenAI articles", n)
        finally:
            session.close()

    return result
