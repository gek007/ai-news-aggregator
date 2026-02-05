from sqlalchemy import inspect
from app.database.session import DATABASE_URL, create_engine
import os


def main():

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=os.getenv("SQL_ECHO", "").lower() in ("1", "true", "yes"),
    )

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(tables)


if __name__ == "__main__":
    main()
