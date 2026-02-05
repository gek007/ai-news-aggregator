"""Drop all database tables. Use when schema changes require recreating tables."""

from dotenv import load_dotenv

from app.database import Base, engine

load_dotenv()

if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped.")
