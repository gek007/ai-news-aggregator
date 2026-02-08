"""Scrapers module for fetching content from various sources"""

from app.scrapers.anthropic_news import AnthropicArticle, AnthropicNewsScraper
from app.scrapers.base import BaseScraper
from app.scrapers.openai_news import OpenAINewsArticle, OpenAINewsScraper
from app.scrapers.rss_base import BaseRSSScraper
from app.scrapers.youtube_rss import ChannelVideo, Transcript, YouTubeRSSScraper

__all__ = [
    "AnthropicArticle",
    "AnthropicNewsScraper",
    "BaseScraper",
    "BaseRSSScraper",
    "ChannelVideo",
    "OpenAINewsArticle",
    "OpenAINewsScraper",
    "Transcript",
    "YouTubeRSSScraper",
]
