"""Base scraper class for all scrapers"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class BaseScraper(ABC):
    """Abstract base class for all scrapers"""

    def __init__(self, source_name: str):
        """
        Initialize the base scraper

        Args:
            source_name: Name of the source being scraped
        """
        self.source_name = source_name

    @abstractmethod
    def fetch_latest(self, **kwargs) -> List[Dict]:
        """
        Fetch latest content from the source

        Returns:
            List of dictionaries containing article/video information
            Each dict should have: title, url, published_at, content/description
        """
        pass

    def filter_by_timeframe(self, items: List[Dict], hours: int = 24) -> List[Dict]:
        """
        Filter items by time frame (last N hours)

        Args:
            items: List of items with 'published_at' datetime
            hours: Number of hours to look back (default: 24)

        Returns:
            Filtered list of items within the timeframe
        """
        if not items:
            return []

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        filtered = []

        for item in items:
            published_at = item.get("published_at")
            if published_at and isinstance(published_at, datetime):
                if published_at >= cutoff_time:
                    filtered.append(item)
            elif published_at and isinstance(published_at, str):
                # Try to parse string datetime
                try:
                    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    if dt >= cutoff_time:
                        filtered.append(item)
                except (ValueError, AttributeError):
                    # If parsing fails, include the item (better to have it than miss it)
                    filtered.append(item)

        return filtered
