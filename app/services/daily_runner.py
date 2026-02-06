"""Daily runner to execute the full pipeline: fetch, digest, rank, email.

Can be run:
- Manually: python -m app.services.daily_runner
- With custom hours: python -m app.services.daily_runner --hours 24
- With custom limit: python -m app.services.daily_runner --limit 10
"""

import argparse
import logging
from typing import Optional

from dotenv import load_dotenv

from app.aggregate import run as aggregate_run
from app.services.digest_service import process_digest
from app.services.email_service import process_email
from app.services.ranking_service import process_rankings

load_dotenv()

logger = logging.getLogger(__name__)


def run_pipeline(hours: int = 24, limit: int = 10) -> dict:
    """
    Run the full pipeline: aggregation -> digest -> ranking -> email.

    Returns:
        Dict with step results.
    """
    results = {}

    logger.info("Step 1/4: Aggregation (hours=%d)", hours)
    results["aggregate"] = aggregate_run(hours=hours, persist=True)

    logger.info("Step 2/4: Digest generation (hours=%d)", hours)
    results["digest"] = process_digest(hours=hours)

    logger.info("Step 3/4: Ranking (hours=%d)", hours)
    results["ranking"] = process_rankings(hours=hours)

    logger.info("Step 4/4: Email (hours=%d, limit=%d)", hours, limit)
    results["email"] = process_email(hours=hours, limit=limit)

    return results


def main(hours: Optional[int] = None, limit: Optional[int] = None) -> None:
    """CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Run the full daily pipeline: fetch, digest, rank, email."
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Look back period in hours (default: 24)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max number of items to include in email (default: 10)",
    )
    args = parser.parse_args()

    actual_hours = hours if hours is not None else args.hours
    actual_limit = limit if limit is not None else args.limit
    run_pipeline(hours=actual_hours, limit=actual_limit)


if __name__ == "__main__":
    main()
