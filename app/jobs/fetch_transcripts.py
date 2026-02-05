"""Fetch transcripts for YouTube videos that don't have one yet.

Can be run:
- Manually: python -m app.jobs.fetch_transcripts
- As a scheduled job: from app.jobs import fetch_transcripts; fetch_transcripts()
- With custom limit: python -m app.jobs.fetch_transcripts --limit 50
"""

import argparse
import logging
from typing import Optional

from dotenv import load_dotenv

from app.database import Repository, get_session
from app.scrapers.youtube_rss import YouTubeRSSScraper

load_dotenv()

logger = logging.getLogger(__name__)


def fetch_transcripts(limit: int = 100) -> dict:
    """
    Fetch transcripts for YouTube videos that don't have one yet.

    Args:
        limit: Maximum number of videos to process in one run.

    Returns:
        Dict with counts: {"processed": N, "success": N, "failed": N}
    """
    result = {"processed": 0, "success": 0, "failed": 0}

    session = get_session()
    try:
        repo = Repository(session)
        scraper = YouTubeRSSScraper()

        videos = repo.get_youtube_videos_without_transcript(limit=limit)
        logger.info("Found %d videos without transcript", len(videos))

        for video in videos:
            result["processed"] += 1
            try:
                logger.info(
                    "Fetching transcript for: %s (%s)", video.title[:50], video.video_id
                )
                transcript = scraper.get_transcript(video.video_id)
                if repo.set_youtube_transcript(video.video_id, transcript.text):
                    result["success"] += 1
                    logger.info("Transcript saved for %s", video.video_id)
                else:
                    result["failed"] += 1
                    logger.warning("Could not save transcript for %s", video.video_id)
            except Exception as e:
                result["failed"] += 1
                logger.warning(
                    "Failed to fetch transcript for %s: %s", video.video_id, e
                )

        logger.info(
            "Transcript fetch complete: %d processed, %d success, %d failed",
            result["processed"],
            result["success"],
            result["failed"],
        )
    finally:
        session.close()

    return result


def run(limit: int = 100) -> dict:
    """Alias for fetch_transcripts() for scheduler compatibility."""
    return fetch_transcripts(limit=limit)


def main(limit: Optional[int] = None) -> None:
    """CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Fetch transcripts for YouTube videos without one."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of videos to process (default: 100)",
    )
    args = parser.parse_args()

    actual_limit = limit if limit is not None else args.limit
    result = fetch_transcripts(limit=actual_limit)

    print("=" * 40)
    print(f"Processed: {result['processed']}")
    print(f"Success:   {result['success']}")
    print(f"Failed:    {result['failed']}")
    print("=" * 40)


if __name__ == "__main__":
    main()
