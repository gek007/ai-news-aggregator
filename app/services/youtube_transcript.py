"""YouTube transcript service using youtube-transcript-api."""

import logging
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

logger = logging.getLogger(__name__)


def _video_id_from_url(url: str) -> str | None:
    """Extract video ID from a YouTube URL. Returns None if not a valid YouTube URL."""
    parsed = urlparse(url)
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        if "watch" in parsed.path:
            qs = parse_qs(parsed.query)
            return (qs.get("v") or [None])[0]
    if parsed.hostname == "youtu.be":
        return (parsed.path or "").strip("/") or None
    return None


def get_transcript(video_input: str, *, languages: list[str] | None = None) -> str:
    """
    Fetch transcript for a YouTube video as plain text.

    Args:
        video_input: Either a YouTube video URL (e.g. youtube.com/watch?v=ID or youtu.be/ID)
                     or a raw video ID.
        languages: Optional list of language codes (e.g. ["en", "de"]). Defaults to English.

    Returns:
        Transcript as a single string (snippets joined with spaces).

    Raises:
        ValueError: If video_input is neither a valid URL containing a video ID nor an 11-char video ID.
        youtube_transcript_api exceptions: If transcript cannot be fetched (e.g. disabled, unavailable).
    """
    video_id = video_input.strip()
    if "/" in video_id or "youtu" in video_id.lower():
        extracted = _video_id_from_url(video_id)
        if not extracted:
            raise ValueError(f"Could not extract video ID from URL: {video_id}")
        video_id = extracted

    if len(video_id) != 11:
        raise ValueError(
            f"Invalid video ID: {video_id!r}. YouTube video IDs are 11 characters."
        )

    lang_list = languages if languages is not None else ["en"]
    transcript = YouTubeTranscriptApi().fetch(video_id, languages=lang_list)
    return TextFormatter().format_transcript(transcript)


if __name__ == "__main__":
    # transcript = get_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    transcript = get_transcript("hoxkVNtY3c0")
    print(transcript)
