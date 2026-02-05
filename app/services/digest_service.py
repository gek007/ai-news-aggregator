"""Digest service to process articles and generate summaries.

Can be run:
- Manually: python -m app.services.digest_service
- As a scheduled job: from app.services.digest_service import process_digest; process_digest()
- With custom hours: python -m app.services.digest_service --hours 48
"""

import argparse
import logging
from typing import Optional

from dotenv import load_dotenv

from app.agents.digest_agent import DigestAgent
from app.database import Repository, get_session

load_dotenv()

logger = logging.getLogger(__name__)


def process_digest(hours: int = 24) -> dict:
    """
    Process all articles/videos from the last N hours and create digest summaries.

    Args:
        hours: Look back period in hours.

    Returns:
        Dict with counts: {"processed": N, "success": N, "failed": N, "skipped": N}
    """
    result = {"processed": 0, "success": 0, "failed": 0, "skipped": 0}

    session = get_session()
    try:
        repo = Repository(session)
        agent = DigestAgent()

        # Get articles without digest
        articles = repo.get_articles_without_digest(hours=hours)

        total = (
            len(articles["youtube"])
            + len(articles["openai"])
            + len(articles["anthropic"])
        )
        logger.info(
            "Found %d items to process: YouTube=%d, OpenAI=%d, Anthropic=%d",
            total,
            len(articles["youtube"]),
            len(articles["openai"]),
            len(articles["anthropic"]),
        )

        # Process YouTube videos
        for video in articles["youtube"]:
            result["processed"] += 1
            try:
                # Skip if no transcript and no description
                if not video.transcript and not video.description:
                    logger.info("Skipping video %s (no content)", video.video_id)
                    result["skipped"] += 1
                    continue

                logger.info("Summarizing YouTube: %s", video.title[:50])
                summary = agent.summarize_youtube(
                    title=video.title,
                    transcript=video.transcript,
                    description=video.description,
                )
                repo.add_digest_item(
                    source_type="youtube",
                    source_id=video.id,
                    url=video.url,
                    title=video.title,
                    summary=summary,
                    published_at=video.published_at,
                )
                result["success"] += 1
            except Exception as e:
                logger.error(
                    "Failed to process YouTube video %s: %s", video.video_id, e
                )
                result["failed"] += 1

        # Process OpenAI articles
        for article in articles["openai"]:
            result["processed"] += 1
            try:
                # Skip if no markdown and no description
                if not article.markdown and not article.description:
                    logger.info("Skipping OpenAI article %s (no content)", article.url)
                    result["skipped"] += 1
                    continue

                logger.info("Summarizing OpenAI: %s", article.title[:50])
                summary = agent.summarize_article(
                    title=article.title,
                    markdown=article.markdown,
                    description=article.description,
                )
                repo.add_digest_item(
                    source_type="openai",
                    source_id=article.id,
                    url=article.url,
                    title=article.title,
                    summary=summary,
                    published_at=article.published_at,
                )
                result["success"] += 1
            except Exception as e:
                logger.error("Failed to process OpenAI article %s: %s", article.url, e)
                result["failed"] += 1

        # Process Anthropic articles
        for article in articles["anthropic"]:
            result["processed"] += 1
            try:
                # Skip if no markdown and no description
                if not article.markdown and not article.description:
                    logger.info(
                        "Skipping Anthropic article %s (no content)", article.url
                    )
                    result["skipped"] += 1
                    continue

                logger.info("Summarizing Anthropic: %s", article.title[:50])
                summary = agent.summarize_article(
                    title=article.title,
                    markdown=article.markdown,
                    description=article.description,
                )
                repo.add_digest_item(
                    source_type="anthropic",
                    source_id=article.id,
                    url=article.url,
                    title=article.title,
                    summary=summary,
                    published_at=article.published_at,
                )
                result["success"] += 1
            except Exception as e:
                logger.error(
                    "Failed to process Anthropic article %s: %s", article.url, e
                )
                result["failed"] += 1

        logger.info(
            "Digest processing complete: %d processed, %d success, %d failed, %d skipped",
            result["processed"],
            result["success"],
            result["failed"],
            result["skipped"],
        )
    finally:
        session.close()

    return result


def run(hours: int = 24) -> dict:
    """Alias for process_digest() for scheduler compatibility."""
    return process_digest(hours=hours)


def main(hours: Optional[int] = None) -> None:
    """CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Process articles and generate digest summaries."
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Look back period in hours (default: 24)",
    )
    args = parser.parse_args()

    actual_hours = hours if hours is not None else args.hours
    result = process_digest(hours=actual_hours)

    print("=" * 40)
    print(f"Processed: {result['processed']}")
    print(f"Success:   {result['success']}")
    print(f"Failed:    {result['failed']}")
    print(f"Skipped:   {result['skipped']}")
    print("=" * 40)


if __name__ == "__main__":
    main()
