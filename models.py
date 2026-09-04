from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FeedItem:
    title: str
    link: str
    guid: str
    published: datetime
    description_html: str
    guid_permalink: bool = True


@dataclass(frozen=True)
class Source:
    title: str
    description: str
    link: str
    output_filename: str
    scrape: Callable[[], list[FeedItem]]
