"""Test script for YouTube RSS scraper"""

import logging
from app.scrapers.youtube_rss import YouTubeRSSScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    """Test YouTube RSS scraper"""
    scraper = YouTubeRSSScraper()

    # Example YouTube channel IDs (you can replace these with your own)
    # To get a channel ID, you can:
    # 1. Go to the channel page
    # 2. View page source and search for "channelId"
    # 3. Or use: https://www.youtube.com/@channelname -> look at the RSS feed URL

    # Example channels (replace with your own):
    # OpenAI: UCqk3CdGN_j8IR9z4uBbVPSg
    # Anthropic: UCqk3CdGN_j8IR9z4uBbVPSg (example - replace with actual)

    channel_ids = [
        "UCqk3CdGN_j8IR9z4uBbVPSg",  # Example - replace with actual channel IDs
    ]

    print("=" * 60)
    print("Testing YouTube RSS Scraper")
    print("=" * 60)
    print(f"\nFetching videos from {len(channel_ids)} channel(s)...")
    print(f"Looking for videos in the last 24 hours\n")

    # Fetch latest videos from last 24 hours
    videos = scraper.fetch_latest(channel_ids, hours=24)

    if videos:
        print(f"\nFound {len(videos)} video(s) in the last 24 hours:\n")
        for i, video in enumerate(videos, 1):
            print(f"{i}. {video['title']}")
            print(f"   URL: {video['url']}")
            print(f"   Published: {video['published_at']}")
            print(f"   Channel ID: {video.get('channel_id', 'N/A')}")
            print(f"   Video ID: {video.get('video_id', 'N/A')}")
            if video.get("description"):
                desc = (
                    video["description"][:100] + "..."
                    if len(video["description"]) > 100
                    else video["description"]
                )
                print(f"   Description: {desc}")
            print()
    else:
        print("\nNo videos found in the last 24 hours.")
        print("\nTrying to fetch all recent videos (no time filter)...")
        all_videos = []
        for channel_id in channel_ids:
            rss_url = scraper.get_rss_url(channel_id)
            videos = scraper.parse_rss_feed(rss_url)
            all_videos.extend(videos)

        if all_videos:
            print(f"\nFound {len(all_videos)} total recent video(s):\n")
            for i, video in enumerate(all_videos[:5], 1):  # Show first 5
                print(f"{i}. {video['title']}")
                print(f"   URL: {video['url']}")
                print(f"   Published: {video['published_at']}")
                print()
        else:
            print("\nNo videos found. Please check:")
            print("1. Channel IDs are correct")
            print("2. Internet connection")
            print("3. RSS feed URLs are accessible")


if __name__ == "__main__":
    main()
