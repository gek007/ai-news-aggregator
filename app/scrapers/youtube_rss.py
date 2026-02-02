"""YouTube RSS feed scraper"""

import feedparser
import logging
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs

from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class YouTubeRSSScraper(BaseScraper):
    """Scraper for YouTube channels using RSS feeds"""

    def __init__(self):
        """Initialize YouTube RSS scraper"""
        super().__init__("YouTube")

    def get_rss_url(self, channel_id: str) -> str:
        """
        Generate YouTube RSS feed URL from channel ID

        Args:
            channel_id: YouTube channel ID

        Returns:
            RSS feed URL
        """
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    def parse_rss_feed(self, rss_url: str) -> List[Dict]:
        """
        Parse YouTube RSS feed and extract video information

        Args:
            rss_url: URL of the RSS feed

        Returns:
            List of video dictionaries with title, url, published_at, description
        """
        try:
            feed = feedparser.parse(rss_url)

            if feed.bozo:
                logger.warning(
                    f"Feed parsing issues for {rss_url}: {feed.bozo_exception}"
                )

            videos = []
            for entry in feed.entries:
                try:
                    # Parse published date
                    published_at = (
                        datetime(*entry.published_parsed[:6])
                        if hasattr(entry, "published_parsed")
                        else None
                    )

                    video = {
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "published_at": published_at,
                        "description": entry.get("summary", ""),
                        "channel_id": self._extract_channel_id(rss_url),
                        "video_id": self._extract_video_id(entry.get("link", "")),
                    }
                    videos.append(video)
                except Exception as e:
                    logger.error(f"Error parsing video entry: {e}")
                    continue

            return videos

        except Exception as e:
            logger.error(f"Error fetching RSS feed {rss_url}: {e}")
            return []

    def _extract_channel_id(self, rss_url: str) -> Optional[str]:
        """Extract channel ID from RSS URL"""
        try:
            parsed = urlparse(rss_url)
            params = parse_qs(parsed.query)
            return params.get("channel_id", [None])[0]
        except Exception:
            return None

    def _extract_video_id(self, video_url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        try:
            parsed = urlparse(video_url)
            if parsed.hostname in ["www.youtube.com", "youtube.com", "youtu.be"]:
                if "watch" in parsed.path:
                    params = parse_qs(parsed.query)
                    return params.get("v", [None])[0]
                elif parsed.hostname == "youtu.be":
                    return parsed.path.lstrip("/")
        except Exception:
            return None
        return None

    def fetch_latest(self, channel_ids: List[str], hours: int = 24) -> List[Dict]:
        """
        Fetch latest videos from multiple YouTube channels

        Args:
            channel_ids: List of YouTube channel IDs
            hours: Number of hours to look back (default: 24)

        Returns:
            List of video dictionaries filtered by timeframe
        """
        all_videos = []

        for channel_id in channel_ids:
            rss_url = self.get_rss_url(channel_id)
            logger.info(f"Fetching videos from channel {channel_id}")

            videos = self.parse_rss_feed(rss_url)
            all_videos.extend(videos)

        # Filter by timeframe
        filtered_videos = self.filter_by_timeframe(all_videos, hours=hours)

        logger.info(
            f"Found {len(filtered_videos)} videos in the last {hours} hours from {len(channel_ids)} channels"
        )

        return filtered_videos


if __name__ == "__main__":
    scraper = YouTubeRSSScraper()
    videos = scraper.fetch_latest(["UCc-FovAyBAQDw2Y7PQ_v0Zw"], hours=24)
    print(videos)
