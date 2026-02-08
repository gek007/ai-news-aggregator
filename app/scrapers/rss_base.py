"""Shared RSS scraper helpers for feed-based sources."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Callable, Iterable, Optional, TypeVar

import feedparser
import trafilatura

from app.scrapers.base import BaseScraper
from app.services.xml_to_markdown import xml_to_markdown as _xml_to_markdown

T = TypeVar("T")


class BaseRSSScraper(BaseScraper):
    """Base class with common RSS parsing helpers."""

    def __init__(self, source_name: str):
        super().__init__(source_name)
        self.logger = logging.getLogger(self.__class__.__name__)

    def _parse_feed(self, rss_url: str):
        feed = feedparser.parse(rss_url)
        if feed.bozo:
            self.logger.warning(
                "Feed parsing issues for %s: %s", rss_url, feed.bozo_exception
            )
        return feed

    def parse_rss_feed(
        self,
        rss_url: str,
        entry_parser: Callable[[object], T],
    ) -> list[T]:
        """
        Parse an RSS feed and return parsed items using entry_parser.

        Args:
            rss_url: URL of the RSS feed.
            entry_parser: Function that converts a feed entry into a model.

        Returns:
            List of parsed items.
        """
        try:
            feed = self._parse_feed(rss_url)
            items: list[T] = []
            for entry in feed.entries:
                try:
                    items.append(entry_parser(entry))
                except Exception as exc:
                    self.logger.error("Error parsing feed entry: %s", exc)
            return items
        except Exception as exc:
            self.logger.error("Error fetching RSS feed %s: %s", rss_url, exc)
            return []

    def _parse_published_at(self, entry: object) -> Optional[datetime]:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        return None

    def _parse_category(self, entry: object) -> Optional[str]:
        if hasattr(entry, "tags") and entry.tags:
            return entry.tags[0].get("term") or entry.tags[0].get("label")
        return None

    def _filter_models_by_timeframe(
        self,
        items: Iterable[object],
        *,
        hours: int,
        model_cls: Callable[..., T],
    ) -> list[T]:
        dicts = [i.model_dump(mode="python") for i in items]
        filtered_dicts = self.filter_by_timeframe(dicts, hours=hours)
        return [model_cls(**d) for d in filtered_dicts]

    def xml_to_markdown(
        self,
        xml_content: str,
        *,
        root_title: Optional[str] = None,
        max_heading_level: int = 6,
    ) -> str:
        """Convert XML string to a human-readable markdown representation."""
        return _xml_to_markdown(
            xml_content,
            root_title=root_title,
            max_heading_level=max_heading_level,
        )

    def url_to_markdown(
        self,
        url: str,
        *,
        timeout: int = 10,
        root_title: Optional[str] = None,
        max_heading_level: int = 6,
    ) -> str:
        """
        Fetch a URL and convert its content to markdown.

        Uses trafilatura; if no main content is found (e.g. XML/RSS), falls back
        to the shared xml_to_markdown converter.
        """
        downloaded = trafilatura.fetch_url(url, timeout=timeout)
        if not downloaded:
            raise ValueError(f"Could not fetch URL: {url}")
        markdown = trafilatura.extract(downloaded, output_format="markdown")
        if markdown:
            return markdown
        try:
            return self.xml_to_markdown(
                downloaded,
                root_title=root_title,
                max_heading_level=max_heading_level,
            )
        except ET.ParseError:
            return downloaded
