"""YouTube RSS feed scraper with optional transcript fetching."""

import feedparser
import logging
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse, parse_qs

from pydantic import BaseModel

from app.scrapers.base import BaseScraper
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

logger = logging.getLogger(__name__)


class ChannelVideo(BaseModel):
    """A video from a YouTube channel (RSS feed entry)."""

    title: str
    url: str
    published_at: Optional[datetime] = None
    description: str
    video_id: Optional[str] = None
    channel_id: Optional[str] = None


class Transcript(BaseModel):
    """Transcript text for a YouTube video."""

    text: str


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

    def parse_rss_feed(self, rss_url: str) -> List[ChannelVideo]:
        """
        Parse YouTube RSS feed and extract video information

        Args:
            rss_url: URL of the RSS feed

        Returns:
            List of ChannelVideo models
        """
        try:
            feed = feedparser.parse(rss_url)

            if feed.bozo:
                logger.warning(
                    f"Feed parsing issues for {rss_url}: {feed.bozo_exception}"
                )

            videos: List[ChannelVideo] = []
            for entry in feed.entries:
                try:
                    published_at = (
                        datetime(*entry.published_parsed[:6])
                        if hasattr(entry, "published_parsed")
                        else None
                    )
                    video = ChannelVideo(
                        title=entry.get("title", ""),
                        url=entry.get("link", ""),
                        published_at=published_at,
                        description=entry.get("summary", ""),
                        video_id=self._extract_video_id(entry.get("link", "")),
                    )
                    videos.append(video)
                except Exception as e:
                    logger.error(f"Error parsing video entry: {e}")
                    continue

            return videos

        except Exception as e:
            logger.error(f"Error fetching RSS feed {rss_url}: {e}")
            return []

    def _extract_video_id(self, video_url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        try:
            parsed = urlparse(video_url)
            if parsed.hostname in ["www.youtube.com", "youtube.com", "youtu.be"]:
                if "watch" in parsed.path:
                    params = parse_qs(parsed.query)
                    return params.get("v", [None])[0]
                if parsed.hostname == "youtu.be":
                    return parsed.path.lstrip("/")
        except Exception:
            return None
        return None

    def get_transcript(
        self,
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

        Raises:
            ValueError: If video_input is not a valid URL or 11-char video ID.
        """
        video_id = video_input.strip()
        if "/" in video_id or "youtu" in video_id.lower():
            extracted = self._extract_video_id(video_id)
            if not extracted:
                raise ValueError(f"Could not extract video ID from URL: {video_id}")
            video_id = extracted
        if len(video_id) != 11:
            raise ValueError(
                f"Invalid video ID: {video_id!r}. YouTube video IDs are 11 characters."
            )
        lang_list = languages if languages is not None else ["en"]
        raw = YouTubeTranscriptApi().fetch(video_id, languages=lang_list)
        text = TextFormatter().format_transcript(raw)
        return Transcript(text=text)

    def fetch_latest(
        self, channel_ids: List[str], hours: int = 24
    ) -> List[ChannelVideo]:
        """
        Fetch latest videos from multiple YouTube channels

        Args:
            channel_ids: List of YouTube channel IDs
            hours: Number of hours to look back (default: 24)

        Returns:
            List of ChannelVideo models filtered by timeframe
        """
        all_videos: List[ChannelVideo] = []

        for channel_id in channel_ids:
            rss_url = self.get_rss_url(channel_id)
            logger.info(f"Fetching videos from channel {channel_id}")

            videos = self.parse_rss_feed(rss_url)
            for v in videos:
                v.channel_id = channel_id
                all_videos.append(v)

        # Filter by timeframe (base expects list of dicts)
        dicts = [v.model_dump(mode="python") for v in all_videos]
        filtered_dicts = self.filter_by_timeframe(dicts, hours=hours)
        filtered_videos = [ChannelVideo(**d) for d in filtered_dicts]

        logger.info(
            f"Found {len(filtered_videos)} videos in the last {hours} hours from {len(channel_ids)} channels"
        )

        return filtered_videos


if __name__ == "__main__":
    scraper = YouTubeRSSScraper()
    videos = scraper.fetch_latest(["UCc-FovAyBAQDw2Y7PQ_v0Zw"], hours=24)
    for video in videos:
        print("------------")
        print("title: ", video.title)
        print("url: ", video.url)
        print("published_at: ", video.published_at)
        print("description: ", video.description)
        print("video_id: ", video.video_id)
        print("transcript: ", scraper.get_transcript(video.video_id).text[:100])
        print("\n\n")

    # print(videos)
    # transcript = scraper.get_transcript("hoxkVNtY3c0")
    # print(transcript)
