"""Entry point: run the full daily pipeline for the last N hours."""

import logging

from app.services.daily_runner import run_pipeline


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    hours = 24
    limit = 10
    run_pipeline(hours=hours, limit=limit)


if __name__ == "__main__":
    main()
    print("Done")
