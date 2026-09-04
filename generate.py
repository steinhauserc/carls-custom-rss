from pathlib import Path

from rss import write_feed
from sources import SOURCES

FEEDS_DIR = Path("feeds")


def main() -> None:
    for source in SOURCES:
        items = source.scrape()
        path = write_feed(source, items, FEEDS_DIR / source.output_filename)
        print(f"Wrote {len(items)} items to {path}")


if __name__ == "__main__":
    main()
