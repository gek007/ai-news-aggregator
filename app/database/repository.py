"""Repository for persisting and querying aggregated content."""

import logging
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database.models import AnthropicArticle, OpenAINewsArticle, YouTubeVideo

logger = logging.getLogger(__name__)


class Repository:
    """Single place to persist and read scraped content."""

    def __init__(self, session: Session):
        self.session = session

    def add_youtube_videos(self, videos: List[Any]) -> int:
        """
        Upsert YouTube videos by video_id. Does not overwrite transcript if already set.
        Returns number of rows affected (inserted or updated).
        """
        if not videos:
            return 0
        count = 0
        for v in videos:
            video_id = getattr(v, "video_id", None) or (
                v.get("video_id") if isinstance(v, dict) else None
            )
            if not video_id:
                continue
            stmt = (
                insert(YouTubeVideo)
                .values(
                    video_id=video_id,
                    channel_id=getattr(v, "channel_id", None)
                    or (v.get("channel_id") if isinstance(v, dict) else None),
                    title=getattr(v, "title", "") or (v.get("title") or ""),
                    url=getattr(v, "url", "") or (v.get("url") or ""),
                    description=getattr(v, "description", None)
                    or (v.get("description") if isinstance(v, dict) else None),
                    published_at=getattr(v, "published_at", None)
                    or (v.get("published_at") if isinstance(v, dict) else None),
                )
                .on_conflict_do_update(
                    index_elements=["video_id"],
                    set_={
                        "channel_id": insert(YouTubeVideo).excluded.channel_id,
                        "title": insert(YouTubeVideo).excluded.title,
                        "url": insert(YouTubeVideo).excluded.url,
                        "description": insert(YouTubeVideo).excluded.description,
                        "published_at": insert(YouTubeVideo).excluded.published_at,
                    },
                )
            )
            self.session.execute(stmt)
            count += 1
        if count:
            self.session.commit()
        return count

    def add_openai_articles(self, articles: List[Any]) -> int:
        """Upsert OpenAI articles by url. Returns number of rows affected."""
        if not articles:
            return 0
        count = 0
        for a in articles:
            url = getattr(a, "url", None) or (
                a.get("url") if isinstance(a, dict) else None
            )
            if not url:
                continue
            stmt = (
                insert(OpenAINewsArticle)
                .values(
                    url=url,
                    title=getattr(a, "title", "") or (a.get("title") or ""),
                    description=getattr(a, "description", None)
                    or (a.get("description") if isinstance(a, dict) else None),
                    published_at=getattr(a, "published_at", None)
                    or (a.get("published_at") if isinstance(a, dict) else None),
                    category=getattr(a, "category", None)
                    or (a.get("category") if isinstance(a, dict) else None),
                    markdown=getattr(a, "markdown", None)
                    or (a.get("markdown") if isinstance(a, dict) else None),
                )
                .on_conflict_do_update(
                    index_elements=["url"],
                    set_={
                        "title": insert(OpenAINewsArticle).excluded.title,
                        "description": insert(OpenAINewsArticle).excluded.description,
                        "published_at": insert(OpenAINewsArticle).excluded.published_at,
                        "category": insert(OpenAINewsArticle).excluded.category,
                        "markdown": insert(OpenAINewsArticle).excluded.markdown,
                    },
                )
            )
            self.session.execute(stmt)
            count += 1
        if count:
            self.session.commit()
        return count

    def add_anthropic_articles(self, articles: List[Any]) -> int:
        """Upsert Anthropic articles by url. Returns number of rows affected."""
        if not articles:
            return 0
        count = 0
        for a in articles:
            url = getattr(a, "url", None) or (
                a.get("url") if isinstance(a, dict) else None
            )
            if not url:
                continue
            stmt = (
                insert(AnthropicArticle)
                .values(
                    url=url,
                    title=getattr(a, "title", "") or (a.get("title") or ""),
                    description=getattr(a, "description", None)
                    or (a.get("description") if isinstance(a, dict) else None),
                    published_at=getattr(a, "published_at", None)
                    or (a.get("published_at") if isinstance(a, dict) else None),
                    category=getattr(a, "category", None)
                    or (a.get("category") if isinstance(a, dict) else None),
                    feed=getattr(a, "feed", None)
                    or (a.get("feed") if isinstance(a, dict) else None),
                    markdown=getattr(a, "markdown", None)
                    or (a.get("markdown") if isinstance(a, dict) else None),
                )
                .on_conflict_do_update(
                    index_elements=["url"],
                    set_={
                        "title": insert(AnthropicArticle).excluded.title,
                        "description": insert(AnthropicArticle).excluded.description,
                        "published_at": insert(AnthropicArticle).excluded.published_at,
                        "category": insert(AnthropicArticle).excluded.category,
                        "feed": insert(AnthropicArticle).excluded.feed,
                        "markdown": insert(AnthropicArticle).excluded.markdown,
                    },
                )
            )
            self.session.execute(stmt)
            count += 1
        if count:
            self.session.commit()
        return count

    def get_youtube_videos_without_transcript(
        self, limit: int = 100
    ) -> List[YouTubeVideo]:
        """Return YouTube videos that have no transcript yet (for backfill job)."""
        stmt = (
            select(YouTubeVideo).where(YouTubeVideo.transcript.is_(None)).limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def set_youtube_transcript(self, video_id: str, transcript: str) -> bool:
        """Set transcript for a video. Returns True if a row was updated."""
        row = (
            self.session.execute(
                select(YouTubeVideo).where(YouTubeVideo.video_id == video_id)
            )
            .scalars()
            .one_or_none()
        )
        if row is None:
            return False
        row.transcript = transcript
        self.session.commit()
        return True
