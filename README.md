https://openai.com/news/

https://www.anthropic.com/research

https://www.anthropic.com/engineering

youtube:

UCW6QeFhV3uUJi0fvjYdkqzg

UCc-FovAyBAQDw2Y7PQ_v0Zw

==========================

How ro run it:

DB:
"postgresql://postgres:postgres@localhost:5432/ai_news_aggregator",


# drop tables

1. uv run .\app\database\drop_tables.py

# create all tables

2. uv run .\app\database\create_tables.py

# run scrapers

3. uv run .\main.py

# get trascript from youtube video

4. uv run .\app\jobs\fetch_transcripts.py

# create summary

5. uv run .\app\services\digest_service.py

# ranking digest news according to user profile  
6.uv run .app\services\ranking_service.py

# send digest to defined email: 
7. python -m app.services.email_service --hours 24 --limit 10

