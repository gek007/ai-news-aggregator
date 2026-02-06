"""Ranking agent to personalize digest items for a user profile."""

import json
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
load_dotenv(".env.local", override=True)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a news ranking assistant.

Goal:
- Rank the provided digest items from most relevant to least relevant for the given user profile.

Ranking rules:
- Use ONLY the provided item data (title, summary, key topics, content category, source).
- Prioritize alignment with the user's interests and preferred content types.
- De-prioritize items that match the user's avoid topics.
- Provide a 0-100 relevance score per item.
- Provide a brief, concrete reason for each score.
- Return every item exactly once, sorted from highest to lowest relevance.
"""


class RankedDigestItem(BaseModel):
    """Single ranked digest item."""

    digest_id: int = Field(description="ID of the digest item")
    score: int = Field(description="Relevance score (0-100)", ge=0, le=100)
    reason: str = Field(
        description="Short explanation of why this item was ranked at this score"
    )


class RankingResult(BaseModel):
    """Structured output for ranking results."""

    ranked_items: list[RankedDigestItem] = Field(
        description="Digest items ranked from most to least relevant"
    )


class RankingAgent:
    """Agent that ranks digest items using OpenAI GPT-4.1 Mini with structured output."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-mini"):
        """
        Initialize the ranking agent.

        Args:
            api_key: OpenAI API key. If not provided, reads from OPENAI_API_KEY env var.
            model: Model to use (default: gpt-4.1-mini).
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def rank_digest_items(
        self,
        user_profile: dict,
        digest_items: list[dict],
    ) -> RankingResult:
        """
        Rank digest items for the provided user profile.

        Args:
            user_profile: Dict with user profile fields.
            digest_items: List of digest item dicts with summary fields.

        Returns:
            RankingResult with ranked items.
        """
        user_message = {
            "user_profile": user_profile,
            "digest_items": digest_items,
        }

        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=SYSTEM_PROMPT,
                input=[
                    {"role": "user", "content": json.dumps(user_message)},
                ],
                text_format=RankingResult,
            )
            result = response.output_parsed
            logger.info("Ranked %d digest items", len(result.ranked_items))
            return result
        except Exception as e:
            logger.error("Failed to rank digest items: %s", e)
            raise


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    agent = RankingAgent()
    test_profile = {
        "name": "Alex",
        "interests": [
            "LLM tooling",
            "AI safety",
            "evaluation",
            "open-source",
            "AI Agent",
        ],
        "avoid_topics": ["crypto", "marketing"],
        "preferred_content_types": ["research", "tutorial"],
    }
    test_items = [
        {
            "digest_id": 1,
            "title": "New LLM evaluation benchmark",
            "summary": "A new benchmark for LLMs focuses on reasoning and robustness.",
            "key_topics": ["evaluation", "benchmarks"],
            "content_category": "research",
            "source_type": "openai",
        },
        {
            "digest_id": 2,
            "title": "AI marketing trends",
            "summary": "A look at how AI is used in marketing campaigns.",
            "key_topics": ["marketing"],
            "content_category": "news",
            "source_type": "anthropic",
        },
    ]
    result = agent.rank_digest_items(test_profile, test_items)
    for item in result.ranked_items:
        print(item)
