"""YouTube transcript service (delegates to YouTubeRSSScraper)."""

import logging
from typing import List, Optional

from app.scrapers.youtube_rss import Transcript, YouTubeRSSScraper

logger = logging.getLogger(__name__)

_scraper = YouTubeRSSScraper()


def get_transcript(
    video_input: str,
    *,
    languages: Optional[List[str]] = None,
) -> Transcript:
    """
    Fetch transcript for a YouTube video.

    Args:
        video_input: YouTube video URL (e.g. youtube.com/watch?v=ID or youtu.be/ID)
                     or an 11-character video ID.
        languages: Optional list of language codes (e.g. ["en", "de"]). Defaults to English.

    Returns:
        Transcript model with text field.
    """
    return _scraper.get_transcript(video_input, languages=languages)
