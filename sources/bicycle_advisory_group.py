from datetime import datetime, timezone
from html import escape
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from fetch import fetch_html
from models import FeedItem, Source

PAGE_URL = "https://www.howardcountymd.gov/boards-commissions/bicycle-advisory-group"
SECTION_TITLE = "2026 Meeting Materials"
DATE_FORMAT = "%B %d, %Y"


def parse_meeting_materials(html: str, page_url: str = PAGE_URL) -> list[FeedItem]:
    soup = BeautifulSoup(html, "html.parser")
    panel = _find_section_panel(soup)
    meetings: list[FeedItem] = []
    current_date: datetime | None = None
    current_links: list[tuple[str, str]] = []

    def flush() -> None:
        if current_date is None:
            return
        meetings.append(_item_from_meeting(current_date, current_links, page_url))

    for paragraph in panel.find_all("p"):
        date = _date_from_paragraph(paragraph)
        if date is not None:
            flush()
            current_date = date
            current_links = []
            continue

        current_links.extend(_links_from_paragraph(paragraph, page_url))

    flush()

    if not meetings:
        raise ValueError(f"No meeting dates found in {SECTION_TITLE!r}")

    return meetings


def scrape() -> list[FeedItem]:
    return parse_meeting_materials(fetch_html(PAGE_URL))


def _find_section_panel(soup: BeautifulSoup) -> Tag:
    for heading in soup.select(".accordion-item__title"):
        if heading.get_text(" ", strip=True) != SECTION_TITLE:
            continue
        article = heading.find_parent("article")
        if article is None:
            break
        panel = article.select_one(".accordion-item__panel")
        if panel is None:
            break
        return panel
    raise ValueError(f"Accordion section {SECTION_TITLE!r} not found")


def _date_from_paragraph(paragraph: Tag) -> datetime | None:
    strong = paragraph.find("strong")
    if strong is None:
        return None
    text = strong.get_text(" ", strip=True)
    try:
        parsed = datetime.strptime(text, DATE_FORMAT)
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc)


def _links_from_paragraph(paragraph: Tag, page_url: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    for anchor in paragraph.find_all("a", href=True):
        label = anchor.get_text(" ", strip=True)
        href = urljoin(page_url, anchor["href"])
        if label and href:
            links.append((label, href))
    return links


def _item_from_meeting(
    meeting_date: datetime,
    links: list[tuple[str, str]],
    page_url: str,
) -> FeedItem:
    date_label = f"{meeting_date.strftime('%B')} {meeting_date.day}, {meeting_date.year}"
    slug = meeting_date.strftime("%Y-%m-%d")
    return FeedItem(
        title=f"HoCo BAG meeting — {date_label}",
        link=page_url,
        guid=f"{page_url}#meeting-{slug}",
        published=meeting_date,
        description_html=_description_html(links),
        guid_permalink=False,
    )


def _description_html(links: list[tuple[str, str]]) -> str:
    if not links:
        return "<p>No materials posted yet.</p>"
    items = "".join(
        f'<li><a href="{escape(href, quote=True)}">{escape(label)}</a></li>'
        for label, href in links
    )
    return f"<ul>{items}</ul>"


SOURCE = Source(
    title="Howard County Bicycle Advisory Group",
    description="Meeting agendas, presentations, and minutes for the Howard County Bicycle Advisory Group.",
    link=PAGE_URL,
    output_filename="bicycle-advisory-group.xml",
    scrape=scrape,
)
