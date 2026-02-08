---
name: AI News Aggregator Implementation
overview: Build a Python-based AI news aggregator that scrapes YouTube channels (via RSS) and blog posts, stores them in PostgreSQL, and generates daily OpenAI-powered email digests with user-customized insights.
todos: []
isProject: false
---

# AI News Aggregator Implementation Plan

## Project Structure

```
ai-news-aggregator/
├── app/
│   ├── __init__.py
│   ├── models.py              # SQLAlchemy database models
│   ├── database.py            # Database connection and session management
│   ├── config.py              # Configuration management
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── llm_service.py     # OpenAI LLM integration for summaries
│   │   └── prompts/           # Prompt templates and files
│   │       ├── summary_prompt.txt
│   │       └── insights_prompt.txt
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py            # Base scraper class
│   │   ├── youtube_rss.py     # YouTube RSS feed scraper
│   │   └── blog.py            # Unified blog scraper (OpenAI, Anthropic, etc.)
│   ├── services/
│   │   ├── __init__.py
│   │   └── email_service.py   # SMTP email sender
│   ├── digest/
│   │   ├── __init__.py
│   │   ├── generator.py       # Daily digest generator
│   │   └── insights.py        # User-customized insights generator
│   └── scheduler.py           # APScheduler setup for daily runs
├── docker/
│   └── docker-compose.yml     # PostgreSQL database setup
├── main.py                    # Entry point
├── pyproject.toml             # Dependencies
├── .env.example               # Environment variables template
└── README.md                  # Documentation
```

## Database Schema

**Sources Table:**

- `id` (Primary Key)
- `name` (e.g., "OpenAI Blog", "Anthropic Blog", "YouTube Channel Name")
- `type` (enum: "youtube", "blog", "rss")
- `url` (source URL)
- `config` (JSON field for source-specific config like RSS feed URL)
- `created_at`, `updated_at`

**Articles Table:**

- `id` (Primary Key)
- `source_id` (Foreign Key to Sources)
- `title`
- `url` (original article/video URL)
- `content` (full text content or transcript)
- `summary` (LLM-generated summary, nullable)
- `insights` (user-customized insights, nullable)
- `published_at` (publication date)
- `scraped_at` (when we scraped it)
- `created_at`, `updated_at`

**User Preferences Table:**

- `id` (Primary Key)
- `email` (unique)
- `insight_style` (JSON field for customization preferences)
- `topics_of_interest` (JSON array of topics/keywords)
- `summary_length` (preference: "short", "medium", "long")
- `created_at`, `updated_at`

## Implementation Steps

### 1. Project Setup & Dependencies

- Update `pyproject.toml` with dependencies:
  - `sqlalchemy` - ORM
  - `psycopg2-binary` - PostgreSQL adapter
  - `python-dotenv` - Environment variables
  - `feedparser` - RSS feed parsing
  - `beautifulsoup4` / `requests` - Web scraping
  - `openai` - LLM integration
  - `apscheduler` - Task scheduling
  - `email-validator` - Email validation

### 2. Docker Database Setup

- Create `docker/docker-compose.yml` with PostgreSQL service
- Include environment variables for database credentials
- Add volume for data persistence

### 3. Database Models (`app/models.py`)

- Define `Source` model with SQLAlchemy
- Define `Article` model with relationship to Source
- Define `UserPreferences` model for customization
- Include timestamps and proper indexes

### 4. Database Connection (`app/database.py`)

- Create database engine and session factory
- Add initialization function to create tables
- Handle connection pooling

### 5. Configuration (`app/config.py`)

- Load environment variables
- Define settings class for:
  - Database connection
  - OpenAI API key
  - Email SMTP settings
  - Source configurations (RSS feed URLs, blog URLs)

### 6. Base Scraper (`app/scrapers/base.py`)

- Abstract base class with common methods
- Standardize article extraction interface

### 7. YouTube RSS Scraper (`app/scrapers/youtube_rss.py`)

- Parse YouTube channel RSS feeds (format: `https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID`)
- Use `feedparser` library to parse RSS feeds
- Extract video metadata (title, description, published date, URL)
- Store as articles with source type "youtube"
- Handle feed parsing errors and rate limiting

### 8. Blog Scraper (`app/scrapers/blog.py`)

- Unified blog scraper that can handle multiple blog sources
- Support for OpenAI blog (blog.openai.com) and Anthropic blog ([www.anthropic.com/news](http://www.anthropic.com/news))
- Extract article title, content, published date, URL
- Store as articles with source type "blog"
- Configurable per source to handle different blog structures
- Use BeautifulSoup for HTML parsing and content extraction

### 9. LLM Service (`app/agent/llm_service.py`)

- Integrate OpenAI API for generating summaries
- Create function to summarize article content
- Create function to generate customized insights based on user preferences
- Handle API errors and rate limits
- Support different summary lengths based on user preferences
- Load prompt templates from `app/agent/prompts/` directory
- Create prompt template files for summaries and insights generation

### 10. Email Service (`app/services/email_service.py`)

- SMTP email sender using standard library
- Support Gmail/Outlook SMTP servers
- Format daily digest as HTML email
- Include article snippets with links

### 11. Insights Generator (`app/digest/insights.py`)

- Generate user-customized insights based on preferences
- Filter articles by topics of interest
- Apply insight style preferences (e.g., "technical", "business-focused", "casual")
- Generate personalized summaries and key takeaways

### 12. Daily Digest Generator (`app/digest/generator.py`)

- Query articles from last 24 hours
- Group by source
- Generate LLM summaries for each article
- Apply user-customized insights using insights generator
- Format digest with:
  - Date range
  - Articles grouped by source
  - Short snippet + link for each
  - Customized insights based on user preferences
  - Clean HTML formatting

### 13. Scheduler (`app/scheduler.py`)

- Setup APScheduler with daily trigger
- Schedule digest generation and email sending
- Include error handling and logging

### 14. Main Entry Point (`main.py`)

- Initialize database
- Register scrapers
- Run initial scrape
- Start scheduler
- Provide CLI interface for manual operations

### 15. Agent Folder Setup

- Create `app/agent/` folder structure
- Create `app/agent/prompts/` folder for prompt templates
- Move LLM service logic to `app/agent/llm_service.py`
- Create prompt template files for:
  - Article summaries
  - User-customized insights
  - Digest generation

### 16. Environment Configuration

- Create `.env.example` with all required variables
- Document configuration in README

## Key Features

- **RSS-based scraping**: Use RSS feeds for YouTube channels (no API key required)
- **Extensible scraper architecture**: Easy to add new sources
- **User customization**: Personalized insights based on topics of interest and style preferences
- **Deduplication**: Prevent duplicate articles based on URL
- **Error handling**: Robust error handling for API calls and scraping
- **Logging**: Comprehensive logging for debugging
- **Configuration**: Environment-based configuration for easy deployment

## Data Flow

1. **Scraping Phase**: Scheduled daily, scrapers fetch new content from all sources (RSS feeds and blogs)
2. **Storage**: Articles stored in PostgreSQL with source relationships
3. **Digest Generation**:
  - Query recent articles from last 24 hours
  - Generate LLM summaries for each article
  - Apply user-customized insights based on preferences
4. **Email Delivery**: Format personalized digest and send via SMTP

## Configuration Required

- PostgreSQL database credentials
- OpenAI API key
- SMTP email credentials (sender email/password)
- Recipient email address
- List of YouTube channel RSS feed URLs
- List of blog URLs to monitor (e.g., blog.openai.com, [www.anthropic.com/news](http://www.anthropic.com/news))

