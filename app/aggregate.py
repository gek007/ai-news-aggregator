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
    Fetch latest content from all sources for the last N hours.

    - YouTube: channels from app.config.YOUTUBE_CHANNEL_IDS
    - Anthropic: fixed news/engineering/research feeds
    - OpenAI: fixed news RSS feed

    Args:
        hours: How far back to look (default: 24).

    Returns:
        Dict with keys "youtube", "anthropic", "openai", each a list of items.
    """
    result: dict[str, List[Any]] = {
        "youtube": [],
        "anthropic": [],
        "openai": [],
    }

    if YOUTUBE_CHANNEL_IDS:
        youtube = YouTubeRSSScraper()
        result["youtube"] = youtube.fetch_latest(YOUTUBE_CHANNEL_IDS, hours=hours)
        logger.info("YouTube: %d items", len(result["youtube"]))
    else:
        logger.info("YouTube: no channels configured, skipping")

    anthropic = AnthropicNewsScraper()
    result["anthropic"] = anthropic.fetch_latest(hours=hours)
    logger.info("Anthropic: %d items", len(result["anthropic"]))

    openai_scraper = OpenAINewsScraper()
    result["openai"] = openai_scraper.fetch_latest(hours=hours)
    logger.info("OpenAI: %d items", len(result["openai"]))

    return result
