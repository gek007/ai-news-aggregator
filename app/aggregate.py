"""Kick-off aggregation: fetch latest from YouTube, Anthropic, and OpenAI."""

import logging
from typing import Any, List

from app.config import YOUTUBE_CHANNEL_IDS
from app.scrapers.anthropic_news import AnthropicNewsScraper
from app.scrapers.openai_news import OpenAINewsScraper
from app.scrapers.youtube_rss import YouTubeRSSScraper

logger = logging.getLogger(__name__)


def run(hours: int = 24) -> dict[str, List[Any]]:
    """
    Collect and return only the newest content from all sources since the last run,
    i.e., within the past N hours (default: 24).

    - YouTube: channels from app.config.YOUTUBE_CHANNEL_IDS
    - Anthropic: fixed news/engineering/research feeds
    - OpenAI: fixed news RSS feed

    Args:
        hours: How far back to look (default: 24).

    Returns:
        Dict with keys "youtube", "anthropic", "openai", each a list of new items found in this run.
    """
    result: dict[str, List[Any]] = {
        "youtube": [],
        "anthropic": [],
        "openai": [],
    }

    # Fetch only newly available videos/articles for each source (nothing historical, only latest)
    if YOUTUBE_CHANNEL_IDS:
        youtube = YouTubeRSSScraper()
        # Only include videos published in the last 'hours'
        result["youtube"] = youtube.fetch_latest(YOUTUBE_CHANNEL_IDS, hours=hours)
        logger.info("YouTube: %d new items in this run", len(result["youtube"]))
    else:
        logger.info("YouTube: no channels configured, skipping")

    anthropic = AnthropicNewsScraper()
    # Only include new articles from the past 'hours'
    result["anthropic"] = anthropic.fetch_latest(hours=hours)
    logger.info("Anthropic: %d new items in this run", len(result["anthropic"]))

    openai_scraper = OpenAINewsScraper()
    # Only include new OpenAI articles from the past 'hours'
    result["openai"] = openai_scraper.fetch_latest(hours=hours)
    logger.info("OpenAI: %d new items in this run", len(result["openai"]))

    return result
