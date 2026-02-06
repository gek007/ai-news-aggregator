"""Ranking service to personalize digest items for a user profile.

Can be run:
- Manually: python -m app.services.ranking_service
- With custom hours: python -m app.services.ranking_service --hours 24
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from app.agents.ranking_agent import RankedDigestItem, RankingAgent
from app.database import Repository, get_session

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_PROFILE_PATH = Path(__file__).resolve().parents[1] / "profiles" / "default_user_profile.json"


def _load_profile_from_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"User profile not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _digest_item_to_payload(item) -> dict:
    key_topics = None
    if item.key_topics:
        try:
            key_topics = json.loads(item.key_topics)
        except Exception:
            key_topics = None
    return {
        "digest_id": item.id,
        "title": item.title,
        "summary": item.summary,
        "key_topics": key_topics,
        "content_category": item.content_category,
        "source_type": item.source_type,
        "published_at": item.published_at.isoformat() if item.published_at else None,
    }


def process_rankings(hours: int = 24) -> dict:
    """
    Rank digest items from the last N hours for the default user profile.

    Returns:
        Dict with counts: {"items": N, "ranked": N, "stored": N}
    """
    result = {"items": 0, "ranked": 0, "stored": 0}

    session = get_session()
    try:
        repo = Repository(session)
        agent = RankingAgent()

        profile_data = _load_profile_from_file(DEFAULT_PROFILE_PATH)
        profile = repo.upsert_user_profile(
            name=profile_data["name"],
            description=profile_data.get("description"),
            interests=profile_data.get("interests"),
            avoid_topics=profile_data.get("avoid_topics"),
            preferred_content_types=profile_data.get("preferred_content_types"),
            preferred_sources=profile_data.get("preferred_sources"),
        )

        digest_items = repo.get_digest_items(hours=hours)
        result["items"] = len(digest_items)
        if not digest_items:
            logger.info("No digest items found in the last %d hours.", hours)
            return result

        payload_items = [_digest_item_to_payload(item) for item in digest_items]
        ranking = agent.rank_digest_items(profile_data, payload_items)

        ranked = list(ranking.ranked_items)
        result["ranked"] = len(ranked)

        ranked_ids = [r.digest_id for r in ranked]
        missing_ids = {item.id for item in digest_items} - set(ranked_ids)
        if missing_ids:
            logger.warning("Model omitted %d items; appending with score 0.", len(missing_ids))
            for missing_id in missing_ids:
                ranked.append(
                    RankedDigestItem(
                        digest_id=missing_id,
                        score=0,
                        reason="Not ranked by model; appended with lowest score.",
                    )
                )

        rankings_to_store = []
        for idx, r in enumerate(ranked, start=1):
            rankings_to_store.append(
                {
                    "digest_item_id": r.digest_id,
                    "rank": idx,
                    "score": int(r.score),
                    "rationale": r.reason,
                }
            )

        result["stored"] = repo.add_digest_rankings(profile.id, rankings_to_store)
        logger.info(
            "Ranking complete: %d items ranked and %d stored.",
            result["ranked"],
            result["stored"],
        )
    finally:
        session.close()

    return result


def run(hours: int = 24) -> dict:
    """Alias for process_rankings() for scheduler compatibility."""
    return process_rankings(hours=hours)


def main(hours: Optional[int] = None) -> None:
    """CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Rank digest items for the default user profile."
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Look back period in hours (default: 24)",
    )
    args = parser.parse_args()

    actual_hours = hours if hours is not None else args.hours
    result = process_rankings(hours=actual_hours)

    print("=" * 40)
    print(f"Items:   {result['items']}")
    print(f"Ranked:  {result['ranked']}")
    print(f"Stored:  {result['stored']}")
    print("=" * 40)


if __name__ == "__main__":
    main()
