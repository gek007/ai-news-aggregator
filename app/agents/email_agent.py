"""Email agent to generate a daily digest email from ranked items."""

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

SYSTEM_PROMPT = """You are an email-writing assistant for an AI news digest.

Goal:
- Produce a friendly, concise email draft using the provided user profile and top-ranked items.

Rules:
- Start with a short greeting using the user's display name.
- Include a 1-2 sentence intro summary of the digest theme.
- List the top items with title, short reason, and URL.
- Keep the tone professional and helpful.
- Do not invent facts or URLs.
"""


class EmailItem(BaseModel):
    """Single email item."""

    rank: int = Field(description="Rank position (1 is best)")
    title: str = Field(description="Item title")
    url: str = Field(description="Item URL")
    summary: str = Field(description="Short summary")
    score: int = Field(description="Relevance score (0-100)", ge=0, le=100)
    reason: str = Field(description="Short reason for inclusion")


class EmailDraft(BaseModel):
    """Structured output for the email draft."""

    subject: str = Field(description="Email subject line")
    greeting: str = Field(description="Greeting line, e.g. 'Hey Dave,'")
    intro: str = Field(description="1-2 sentence intro summary")
    items: list[EmailItem] = Field(description="Top ranked items")
    closing: str = Field(description="Short closing line")


class EmailAgent:
    """Agent that generates a digest email using OpenAI GPT-4.1 Mini."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def generate_email(
        self,
        user_profile: dict,
        ranked_items: list[dict],
        date_str: str,
    ) -> EmailDraft:
        """Generate an email draft."""
        payload = {
            "date": date_str,
            "user_profile": user_profile,
            "ranked_items": ranked_items,
        }
        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=SYSTEM_PROMPT,
                input=[{"role": "user", "content": json.dumps(payload)}],
                text_format=EmailDraft,
            )
            result = response.output_parsed
            logger.info("Generated email draft with %d items", len(result.items))
            return result
        except Exception as e:
            logger.error("Failed to generate email: %s", e)
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = EmailAgent()
    test_profile = {"display_name": "Dave"}
    test_items = [
        {
            "rank": 1,
            "title": "New LLM evaluation benchmark",
            "url": "https://example.com/benchmark",
            "summary": "A new benchmark for LLMs focuses on reasoning and robustness.",
            "score": 92,
            "reason": "Strong alignment with evaluation interests.",
        }
    ]
    draft = agent.generate_email(test_profile, test_items, "February 6, 2026")
    print(draft)
