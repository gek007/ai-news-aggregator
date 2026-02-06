"""Email service to generate a daily digest email from ranked items.

Can be run:
- Manually: python -m app.services.email_service
- With custom hours: python -m app.services.email_service --hours 24
- With custom limit: python -m app.services.email_service --limit 10
"""

import argparse
import json
import logging
import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from app.agents.email_agent import EmailAgent
from app.database import Repository, get_session

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_PROFILE_PATH = (
    Path(__file__).resolve().parents[1] / "profiles" / "default_user_profile.json"
)


def _load_profile_from_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"User profile not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _ranking_row_to_payload(ranking, item) -> dict:
    return {
        "rank": ranking.rank,
        "score": ranking.score,
        "reason": ranking.rationale or "",
        "title": item.title,
        "url": item.url,
        "summary": item.summary,
    }


def _truncate_summary_lines(text: str, max_lines: int = 4) -> str:
    if not text:
        return ""
    if "\n" in text:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        return "\n".join(lines[:max_lines])

    sentences = [s.strip() for s in text.split(".") if s.strip()]
    truncated = ". ".join(sentences[:max_lines])
    if truncated and not truncated.endswith("."):
        truncated += "."
    return truncated


def process_email(hours: int = 24, limit: int = 10) -> dict:
    """
    Generate an email draft from top-ranked digest items.

    Returns:
        Dict with counts: {"items": N, "email_items": N}
    """
    result = {"items": 0, "email_items": 0}

    session = get_session()
    try:
        repo = Repository(session)
        agent = EmailAgent()

        profile_data = _load_profile_from_file(DEFAULT_PROFILE_PATH)
        profile = repo.get_user_profile_by_name(profile_data["name"])
        if profile is None:
            logger.error("User profile not found in DB: %s", profile_data["name"])
            return result

        ranked_rows = repo.get_top_ranked_digest_items(
            user_profile_id=profile.id,
            hours=hours,
            limit=limit,
        )
        if not ranked_rows:
            logger.info("No ranked items found in the last %d hours.", hours)
            return result

        ranked_items = [_ranking_row_to_payload(r, i) for r, i in ranked_rows]
        result["items"] = len(ranked_items)
        result["email_items"] = len(ranked_items)

        date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")
        draft = agent.generate_email(profile_data, ranked_items, date_str)

        _send_email_if_configured(draft)

        print("=" * 40)
        print(f"Subject: {draft.subject}")
        print(draft.greeting)
        print()
        print(draft.intro)
        print()
        for item in draft.items:
            print(f"{item.rank}. {item.title} ({item.score})")
            print(f"- {item.summary}")
            print(f"- {item.reason}")
            print(f"- {item.url}")
            print()
        print(draft.closing)
        print("=" * 40)
    finally:
        session.close()

    return result


def _send_email_if_configured(draft) -> None:
    """Send the email via Gmail SMTP if env vars are set."""
    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
    email_to = os.getenv("EMAIL_TO") or gmail_user

    if not gmail_user or not gmail_app_password:
        logger.info("Gmail SMTP not configured; skipping send.")
        return

    if not email_to:
        logger.warning("EMAIL_TO not set and GMAIL_USER missing; skipping send.")
        return

    msg = EmailMessage()
    msg["Subject"] = "AI digest news"
    msg["From"] = gmail_user
    msg["To"] = email_to

    lines = []
    lines.append(f"**{draft.greeting}**")
    lines.append("")
    lines.append(draft.intro)
    lines.append("")
    lines.append("## Top ranked articles")
    lines.append("")
    for item in draft.items:
        summary = _truncate_summary_lines(item.summary, max_lines=4)
        lines.append(f"{item.rank}. **[{item.title}]({item.url})** (Score: {item.score})")
        if summary:
            lines.append(summary)
        if item.reason:
            lines.append(f"*Why this matters:* {item.reason}")
        lines.append(f"[Read more]({item.url})")
        lines.append("")
    lines.append(draft.closing)
    msg.set_content("\n".join(lines), subtype="markdown")

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(gmail_user, gmail_app_password)
        smtp.send_message(msg)

    logger.info("Email sent to %s", email_to)


def run(hours: int = 24, limit: int = 10) -> dict:
    """Alias for process_email() for scheduler compatibility."""
    return process_email(hours=hours, limit=limit)


def main(hours: Optional[int] = None, limit: Optional[int] = None) -> None:
    """CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Generate a daily digest email from ranked items."
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
        help="Max number of items to include (default: 10)",
    )
    args = parser.parse_args()

    actual_hours = hours if hours is not None else args.hours
    actual_limit = limit if limit is not None else args.limit
    process_email(hours=actual_hours, limit=actual_limit)


if __name__ == "__main__":
    main()
