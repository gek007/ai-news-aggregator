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
