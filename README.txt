AI News Aggregator
==================

Overview
This project collects AI-related updates from OpenAI news, Anthropic news/engineering/research feeds, and a list of YouTube channels. It stores the raw items in Postgres, generates short AI summaries, ranks them against a user profile, and can email a daily digest.

How It Works (Pipeline)
1) Aggregation
   - Scrapers pull RSS entries (OpenAI, Anthropic) and YouTube channel feeds.
   - Items are normalized and stored via the repository layer.
2) Enrichment
   - YouTube transcripts can be fetched for videos (optional).
   - Article pages are converted to markdown for richer summaries.
3) Digest
   - The digest service summarizes new items with the DigestAgent (OpenAI API).
4) Ranking
   - The ranking service scores digest items based on the default user profile JSON.
5) Email
   - The email service composes a daily digest from the top-ranked items and can send via Gmail SMTP.

Key Modules
- app/scrapers: RSS and YouTube scrapers (OpenAI, Anthropic, YouTube).
- app/database: SQLAlchemy models + repository with upserts and queries.
- app/agents: OpenAI-powered summarization, ranking, and email composition.
- app/services: Orchestration for digest, ranking, email, and daily pipeline.

Configuration
- DATABASE_URL: Postgres connection string (defaults to local).
- OPENAI_API_KEY: Required for summarization/ranking/email generation.
- GMAIL_USER / GMAIL_APP_PASSWORD / EMAIL_TO: Optional for SMTP email sending.
- app/config.py: YouTube channel IDs to monitor.
- app/profiles/default_user_profile.json: User preference profile for ranking.

Typical Runs
- Full pipeline: python -m app.services.daily_runner --hours 24 --limit 10
- Just scrape:   python -m app.aggregate
- Digest only:   python -m app.services.digest_service --hours 24
- Rank only:     python -m app.services.ranking_service --hours 24
- Email only:    python -m app.services.email_service --hours 24 --limit 10
