"""SQLAlchemy models for aggregated content."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base for all models."""

    pass


class YouTubeVideo(Base):
    """YouTube video from monitored channels (transcript filled later)."""

    __tablename__ = "youtube_videos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(
        String(16), unique=True, nullable=False, index=True
    )
    channel_id: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class OpenAINewsArticle(Base):
    """OpenAI news article from RSS."""

    __tablename__ = "openai_articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(
        String(1024), unique=True, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    category: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class AnthropicArticle(Base):
    """Anthropic article from news/engineering/research feeds."""

    __tablename__ = "anthropic_articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(
        String(1024), unique=True, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    category: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    feed: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DigestItem(Base):
    """A digest summary item linking to a source article/video."""

    __tablename__ = "digest_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Source type: "youtube", "openai", "anthropic"
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    # Foreign keys to source tables (only one will be set per row)
    youtube_video_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("youtube_videos.id"), nullable=True, index=True
    )
    openai_article_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("openai_articles.id"), nullable=True, index=True
    )
    anthropic_article_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("anthropic_articles.id"), nullable=True, index=True
    )

    # Denormalized fields for quick access
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)

    # AI-generated summary (2-3 sentences)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Structured output fields from OpenAI
    key_topics: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # JSON array stored as text
    content_category: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )  # announcement, tutorial, research, news, opinion, other

    # Metadata
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    youtube_video: Mapped[Optional["YouTubeVideo"]] = relationship(
        "YouTubeVideo", foreign_keys=[youtube_video_id]
    )
    openai_article: Mapped[Optional["OpenAINewsArticle"]] = relationship(
        "OpenAINewsArticle", foreign_keys=[openai_article_id]
    )
    anthropic_article: Mapped[Optional["AnthropicArticle"]] = relationship(
        "AnthropicArticle", foreign_keys=[anthropic_article_id]
    )


class UserProfile(Base):
    """User profile with interests for ranking personalization."""

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # JSON-encoded lists stored as text
    interests: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avoid_topics: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preferred_content_types: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preferred_sources: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DigestRanking(Base):
    """Ranking of digest items for a specific user profile."""

    __tablename__ = "digest_rankings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_profile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_profiles.id"), nullable=False, index=True
    )
    digest_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("digest_items.id"), nullable=False, index=True
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user_profile: Mapped["UserProfile"] = relationship("UserProfile")
    digest_item: Mapped["DigestItem"] = relationship("DigestItem")
