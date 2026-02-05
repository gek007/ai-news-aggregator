https://openai.com/news/

https://www.anthropic.com/research

https://www.anthropic.com/engineering

youtube:

UCW6QeFhV3uUJi0fvjYdkqzg

UCc-FovAyBAQDw2Y7PQ_v0Zw

==========================

How ro run it:

# drop tables

1. uv run .\app\database\drop_tables.py

# create all tables

2. uv run .\app\database\create_tables.py

# run scrapers

3. uv run .\main.py

# get trascript from youtube video

4. uv run app.jobs.fetch_transcripts

# create summary

4. uv run .\app\services\digest_service.py
