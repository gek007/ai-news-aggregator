"""Create all database tables. Run after starting PostgreSQL (e.g. docker compose up -d)."""

from dotenv import load_dotenv

from app.database import create_all_tables

load_dotenv()

if __name__ == "__main__":
    create_all_tables()
    print("Tables created.")
