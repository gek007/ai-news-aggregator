"""Entry point: run aggregation for the last N hours (default 24)."""

import logging

from app.aggregate import run


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    hours = 48
    result = run(hours=hours)
    print("==============")
    print(
        f"\nLast {hours}h: YouTube {len(result['youtube'])} | Anthropic {len(result['anthropic'])} | OpenAI {len(result['openai'])}"
    )


if __name__ == "__main__":
    main()
    print("Done")
