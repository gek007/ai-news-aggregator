"""Entry point: fetch a URL and export its content as markdown."""

from app.scrapers.openai_news import OpenAINewsScraper


def main() -> None:
    scraper = OpenAINewsScraper()
    url = "https://example.com"
    markdown = scraper.url_to_markdown(url)
    print(markdown)


if __name__ == "__main__":
    main()
