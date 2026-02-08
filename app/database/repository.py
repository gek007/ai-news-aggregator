"""Repository for persisting and querying aggregated content."""

import logging
from typing import Any, List

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database.models import (
    AnthropicArticle,
    DigestRanking,
    DigestItem,
    OpenAINewsArticle,
    YouTubeVideo,
    UserProfile,
)

logger = logging.getLogger(__name__)


class Repository:
    """Single place to persist and read scraped content."""

    def __init__(self, session: Session):
        self.session = session

    def _value(self, item: Any, key: str, default: Any = None) -> Any:
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)

    def _upsert_records(
        self,
        model,
        items: List[Any],
        *,
        unique_field: str,
        field_names: List[str],
    ) -> int:
        if not items:
            return 0
        count = 0
        for item in items:
            unique_value = self._value(item, unique_field, None)
            if not unique_value:
                continue
            values = {name: self._value(item, name, None) for name in field_names}
            values[unique_field] = unique_value
            stmt = (
                insert(model)
                .values(**values)
                .on_conflict_do_update(
                    index_elements=[unique_field],
                    set_={
                        name: insert(model).excluded[name]
                        for name in field_names
                        if name != unique_field
                    },
                )
            )
            self.session.execute(stmt)
            count += 1
        if count:
            self.session.commit()
        return count

    def add_youtube_videos(self, videos: List[Any]) -> int:
        """
        Upsert YouTube videos by video_id. Does not overwrite transcript if already set.
        Returns number of rows affected (inserted or updated).
        """
        return self._upsert_records(
            YouTubeVideo,
            videos,
            unique_field="video_id",
            field_names=[
                "video_id",
                "channel_id",
                "title",
                "url",
                "description",
                "published_at",
            ],
        )

    def add_openai_articles(self, articles: List[Any]) -> int:
        """Upsert OpenAI articles by url. Returns number of rows affected."""
        return self._upsert_records(
            OpenAINewsArticle,
            articles,
            unique_field="url",
            field_names=[
                "url",
                "title",
                "description",
                "published_at",
                "category",
                "markdown",
            ],
        )

    def add_anthropic_articles(self, articles: List[Any]) -> int:
        """Upsert Anthropic articles by url. Returns number of rows affected."""
        return self._upsert_records(
            AnthropicArticle,
            articles,
            unique_field="url",
            field_names=[
                "url",
                "title",
                "description",
                "published_at",
                "category",
                "feed",
                "markdown",
            ],
        )

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

    # -------------------------------------------------------------------------
    # Digest methods
    # -------------------------------------------------------------------------

    def get_articles_without_digest(
        self, hours: int = 24
    ) -> dict[str, List[Any]]:
        """
        Get all articles/videos from the last N hours that don't have a digest yet.

        Returns:
            Dict with keys "youtube", "openai", "anthropic", each containing a list.
        """
        from datetime import datetime, timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        # Get IDs that already have digests
        existing_youtube = set(
            self.session.scalars(
                select(DigestItem.youtube_video_id).where(
                    DigestItem.youtube_video_id.isnot(None)
                )
            ).all()
        )
        existing_openai = set(
            self.session.scalars(
                select(DigestItem.openai_article_id).where(
                    DigestItem.openai_article_id.isnot(None)
                )
            ).all()
        )
        existing_anthropic = set(
            self.session.scalars(
                select(DigestItem.anthropic_article_id).where(
                    DigestItem.anthropic_article_id.isnot(None)
                )
            ).all()
        )

        # YouTube videos without digest
        youtube_stmt = select(YouTubeVideo).where(
            YouTubeVideo.created_at >= cutoff,
            YouTubeVideo.id.notin_(existing_youtube) if existing_youtube else True,
        )
        youtube_videos = list(self.session.scalars(youtube_stmt).all())

        # OpenAI articles without digest
        openai_stmt = select(OpenAINewsArticle).where(
            OpenAINewsArticle.created_at >= cutoff,
            OpenAINewsArticle.id.notin_(existing_openai) if existing_openai else True,
        )
        openai_articles = list(self.session.scalars(openai_stmt).all())

        # Anthropic articles without digest
        anthropic_stmt = select(AnthropicArticle).where(
            AnthropicArticle.created_at >= cutoff,
            AnthropicArticle.id.notin_(existing_anthropic) if existing_anthropic else True,
        )
        anthropic_articles = list(self.session.scalars(anthropic_stmt).all())

        return {
            "youtube": youtube_videos,
            "openai": openai_articles,
            "anthropic": anthropic_articles,
        }

    def add_digest_item(
        self,
        source_type: str,
        source_id: int,
        url: str,
        title: str,
        summary: str,
        key_topics: List[str] | None = None,
        content_category: str | None = None,
        published_at: Any = None,
    ) -> DigestItem:
        """
        Add a digest item linking to a source article/video.

        Args:
            source_type: "youtube", "openai", or "anthropic"
            source_id: The ID of the source record
            url: URL to the original content
            title: Title of the content
            summary: AI-generated 2-3 sentence summary
            key_topics: List of key topics from structured output
            content_category: Content type (announcement, tutorial, research, etc.)
            published_at: Original publish date

        Returns:
            The created DigestItem
        """
        import json

        item = DigestItem(
            source_type=source_type,
            youtube_video_id=source_id if source_type == "youtube" else None,
            openai_article_id=source_id if source_type == "openai" else None,
            anthropic_article_id=source_id if source_type == "anthropic" else None,
            url=url,
            title=title,
            summary=summary,
            key_topics=json.dumps(key_topics) if key_topics else None,
            content_category=content_category,
            published_at=published_at,
        )
        self.session.add(item)
        self.session.commit()
        return item

    def get_digest_items(self, hours: int = 24) -> List[DigestItem]:
        """Get digest items from the last N hours."""
        from datetime import datetime, timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = (
            select(DigestItem)
            .where(DigestItem.created_at >= cutoff)
            .order_by(DigestItem.created_at.desc())
        )
        return list(self.session.scalars(stmt).all())

    # -------------------------------------------------------------------------
    # User profile + ranking methods
    # -------------------------------------------------------------------------

    def get_user_profile_by_name(self, name: str) -> UserProfile | None:
        """Get a user profile by name."""
        stmt = select(UserProfile).where(UserProfile.name == name)
        return self.session.scalars(stmt).one_or_none()

    def upsert_user_profile(
        self,
        name: str,
        description: str | None = None,
        interests: list[str] | None = None,
        avoid_topics: list[str] | None = None,
        preferred_content_types: list[str] | None = None,
        preferred_sources: list[str] | None = None,
    ) -> UserProfile:
        """Create or update a user profile."""
        import json

        profile = self.get_user_profile_by_name(name)
        if profile is None:
            profile = UserProfile(name=name)
            self.session.add(profile)

        profile.description = description
        profile.interests = json.dumps(interests) if interests else None
        profile.avoid_topics = json.dumps(avoid_topics) if avoid_topics else None
        profile.preferred_content_types = (
            json.dumps(preferred_content_types) if preferred_content_types else None
        )
        profile.preferred_sources = (
            json.dumps(preferred_sources) if preferred_sources else None
        )

        self.session.commit()
        return profile

    def add_digest_rankings(
        self,
        user_profile_id: int,
        rankings: list[dict[str, Any]],
    ) -> int:
        """
        Persist ranking results for a user profile.

        Args:
            user_profile_id: ID of the user profile
            rankings: List of dicts with keys: digest_item_id, rank, score, rationale

        Returns:
            Number of rankings inserted.
        """
        if not rankings:
            return 0
        count = 0
        for r in rankings:
            item = DigestRanking(
                user_profile_id=user_profile_id,
                digest_item_id=r["digest_item_id"],
                rank=r["rank"],
                score=r["score"],
                rationale=r.get("rationale"),
            )
            self.session.add(item)
            count += 1
        if count:
            self.session.commit()
        return count

    def get_top_ranked_digest_items(
        self,
        user_profile_id: int,
        hours: int = 24,
        limit: int = 10,
    ) -> list[tuple[DigestRanking, DigestItem]]:
        """Return top ranked digest items for a user profile in the last N hours."""
        from datetime import datetime, timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = (
            select(DigestRanking, DigestItem)
            .join(DigestItem, DigestRanking.digest_item_id == DigestItem.id)
            .where(
                DigestRanking.user_profile_id == user_profile_id,
                DigestRanking.created_at >= cutoff,
            )
            .order_by(DigestRanking.rank.asc())
            .limit(limit)
            .options(joinedload(DigestRanking.digest_item))
        )
        return list(self.session.execute(stmt).all())
