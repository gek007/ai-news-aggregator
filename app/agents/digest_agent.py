"""Digest summary agent using OpenAI's Responses API with GPT-4.1 Mini."""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
load_dotenv(".env.local", override=True)

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI news digest assistant. Your role is to create concise, informative summaries of AI-related content.

Your task:
- Read the provided content (article, blog post, or video transcript)
- Create a 2-3 sentence summary that captures the key points
- Focus on what's new, important, or actionable
- Use clear, professional language
- Do not include any preamble like "This article discusses..." - just give the summary directly

The summary should help a busy reader quickly understand what the content is about and whether they should read/watch the full version."""


class DigestAgent:
    """Agent that creates digest summaries using OpenAI GPT-4.1 Mini."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-mini"):
        """
        Initialize the digest agent.

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

    def summarize(
        self,
        content: str,
        title: Optional[str] = None,
        content_type: str = "article",
    ) -> str:
        """
        Generate a 2-3 sentence summary of the content.

        Args:
            content: The full text content to summarize (article markdown or transcript).
            title: Optional title to provide context.
            content_type: Type of content ("article", "video", "blog post").

        Returns:
            A 2-3 sentence summary string.
        """
        # Truncate content if too long (keep under ~12k tokens for safety)
        max_chars = 40000
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n[Content truncated...]"

        user_message = f"Please summarize this {content_type}"
        if title:
            user_message += f' titled "{title}"'
        user_message += f":\n\n{content}"

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=SYSTEM_PROMPT,
                input=user_message,
            )
            summary = response.output_text.strip()
            logger.info(
                "Generated summary for: %s", title[:50] if title else "untitled"
            )
            return summary

        except Exception as e:
            logger.error("Failed to generate summary: %s", e)
            raise

    def summarize_youtube(
        self, title: str, transcript: Optional[str], description: Optional[str] = None
    ) -> str:
        """
        Summarize a YouTube video.

        Args:
            title: Video title.
            transcript: Video transcript (preferred).
            description: Video description (fallback if no transcript).

        Returns:
            A 2-3 sentence summary.
        """
        if transcript:
            content = transcript
        elif description:
            content = f"Video description:\n{description}"
        else:
            content = f"Video titled: {title}"

        return self.summarize(content, title=title, content_type="video")

    def summarize_article(
        self, title: str, markdown: Optional[str], description: Optional[str] = None
    ) -> str:
        """
        Summarize an article (OpenAI or Anthropic).

        Args:
            title: Article title.
            markdown: Full article content in markdown.
            description: Article description/excerpt (fallback).

        Returns:
            A 2-3 sentence summary.
        """
        if markdown:
            content = markdown
        elif description:
            content = description
        else:
            content = f"Article titled: {title}"

        return self.summarize(content, title=title, content_type="article")


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    agent = DigestAgent()

    test_content = """
    OpenAI has announced GPT-5, their most advanced language model yet. 
    The new model shows significant improvements in reasoning, coding, and multimodal capabilities.
    It will be available to ChatGPT Plus subscribers starting next month, with API access following shortly after.
    The model was trained on a larger dataset and uses a new architecture that improves efficiency by 40%.
    """

    summary = agent.summarize(test_content, title="OpenAI Announces GPT-5")
    print(f"Summary: {summary}")
