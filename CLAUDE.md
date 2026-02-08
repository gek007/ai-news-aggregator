# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI News Aggregator - A Python-based pipeline that collects, summarizes, ranks, and emails AI-related news from OpenAI, Anthropic, and YouTube. Uses OpenAI GPT-4.1 Mini for structured summarization and personalization.

**Tech Stack**: Python 3.12+, PostgreSQL with SQLAlchemy, OpenAI API, uv package manager, Docker deployment on Render.com

## Common Commands

### Package Management
```bash
uv pip install -r requirements.txt   # Install dependencies
uv pip freeze                        # List installed packages
uv sync                              # Sync environment
uv add package-name                  # Add a package
```

### Database Operations
```bash
uv run app.database.drop_tables.py   # Drop all tables
uv run app.database.create_tables.py # Create all tables
```

### Running the Pipeline
```bash
# Full pipeline (recommended)
python -m app.services.daily_runner --hours 24 --limit 10

# Or via main.py
uv run main.py

# Individual steps
uv run main.py                        # Aggregation only
uv run app.jobs.fetch_transcripts.py  # Get YouTube transcripts
uv run app.services.digest_service.py # Create summaries
uv run app.services.ranking_service.py # Rank by user profile
python -m app.services.email_service --hours 24 --limit 10 # Send email
```

## Architecture

### Pipeline Flow
```
Aggregation (scrapers) → Digest (AI summaries) → Ranking (personalization) → Email
```

1. **Aggregation** (`app/aggregate.py`): Fetches latest content from all sources
2. **Digest** (`app/services/digest_service.py`): Creates AI summaries with structured output
3. **Ranking** (`app/services/ranking_service.py`): Personalizes based on user profile
4. **Email** (`app/services/email_service.py`): Sends top-ranked items via Gmail SMTP

### Core Components

**Scrapers** (`app/scrapers/`)
- Base class with time-based filtering
- YouTube RSS, OpenAI News, Anthropic News (news/engineering/research feeds)

**Agents** (`app/agents/`)
- `DigestAgent`: OpenAI structured output with GPT-4.1 Mini
- Returns `DigestSummary` with summary, key_topics, content_type
- `RankingAgent`: Personalizes ranking based on user profile

**Repository** (`app/database/repository.py`)
- Centralized data access with upsert operations
- Uses PostgreSQL `INSERT ... ON CONFLICT DO UPDATE` for idempotency
- Key methods: `add_youtube_videos()`, `get_articles_without_digest()`, `add_digest_item()`, `get_top_ranked_digest_items()`

**Database Models** (`app/database/models.py`)
- `YouTubeVideo`, `OpenAINewsArticle`, `AnthropicArticle` - source tables
- `DigestItem` - normalized summaries with foreign keys to sources
- `UserProfile` - JSON-based interests/avoid topics
- `DigestRanking` - rankings per user profile

### User Profiles

Located in `app/profiles/*.json`. Example structure:
```json
{
  "name": "default",
  "interests": ["LLM tooling", "agent frameworks"],
  "avoid_topics": ["crypto", "marketing hype"],
  "preferred_content_types": ["research", "tutorial"],
  "preferred_sources": ["openai", "anthropic", "youtube"]
}
```

## Configuration

- **YouTube Channels**: Edit `app/config.py` → `YOUTUBE_CHANNEL_IDS`
- **Database**: Set `DATABASE_URL` environment variable (PostgreSQL)
- **OpenAI**: Set `OPENAI_API_KEY` environment variable
- **Email**: Gmail credentials via environment variables

## Code Patterns

**Structured Output**: Use `openai.responses.parse()` with Pydantic models for AI responses (see `DigestAgent`).

**Upsert Pattern**: Repository uses PostgreSQL upsert for idempotent writes - same data can be processed multiple times safely.

**Time-based Filtering**: All scrapers filter by `hours` parameter using UTC timestamps.

**CLI Arguments**: Services can be run with `--hours N` and `--limit N` flags.

## Key Files to Understand

- `app/services/daily_runner.py:26` - Pipeline orchestration
- `app/agents/digest_agent.py:62` - AI summarization with structured output
- `app/database/repository.py:149` - Fetching items without digests
- `app/aggregate.py:15` - Multi-source aggregation entry point
