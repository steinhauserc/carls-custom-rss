from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from fetch import fetch_html
from models import FeedItem, Source

LISTING_URL = "https://governor.maryland.gov/news/press-releases"
LISTING_BLOCK_ID = "block-views-block-listing-page-blocks-block-lp-news"


def parse_listing(html: str, base_url: str = LISTING_URL) -> list[FeedItem]:
    soup = BeautifulSoup(html, "html.parser")
    block = soup.find(id=LISTING_BLOCK_ID)
    if block is None:
        raise ValueError(f"Listing block #{LISTING_BLOCK_ID} not found")

    items: list[FeedItem] = []
    for li in block.select("li.maryland-listing-item"):
        title_link = li.select_one("a.maryland-listing-item__title")
        if title_link is None or not title_link.get("href"):
            raise ValueError("Listing item is missing a title link")

        title = title_link.get_text(" ", strip=True)
        if not title:
            raise ValueError("Listing item has an empty title")

        time_el = li.select_one("time[datetime]")
        if time_el is None or not time_el.get("datetime"):
            raise ValueError(f"Listing item is missing a datetime: {title}")

        url = urljoin(base_url, title_link["href"])
        items.append(
            FeedItem(
                title=title,
                link=url,
                guid=url,
                published=_parse_datetime(time_el["datetime"]),
                description_html=title,
            )
        )

    if not items:
        raise ValueError("Listing block contained no press-release items")

    return items


def scrape() -> list[FeedItem]:
    return parse_listing(fetch_html(LISTING_URL))


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


SOURCE = Source(
    title="Maryland Governor Press Releases",
    description="Official press releases from the Office of Governor.",
    link=LISTING_URL,
    output_filename="governor-press-releases.xml",
    scrape=scrape,
)
