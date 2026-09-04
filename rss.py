from pathlib import Path

from feedgen.feed import FeedGenerator

from models import FeedItem, Source


def build_feed(source: Source, items: list[FeedItem]) -> FeedGenerator:
    fg = FeedGenerator()
    fg.title(source.title)
    fg.link(href=source.link, rel="alternate")
    fg.description(source.description)
    fg.language("en")

    # feedgen prepends entries; reverse so the newest listing item stays first.
    for item in reversed(items):
        entry = fg.add_entry()
        entry.title(item.title)
        entry.link(href=item.link)
        entry.guid(item.guid, permalink=item.guid_permalink)
        entry.pubDate(item.published)
        entry.description(item.description_html, isSummary=False)
        entry.content(item.description_html, type="html")

    return fg


def write_feed(source: Source, items: list[FeedItem], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    build_feed(source, items).rss_file(str(output_path), pretty=True)
    return output_path
