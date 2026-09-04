import requests

USER_AGENT = "howard-county-rss (custom feed scraper)"
TIMEOUT_SECONDS = 30


def fetch_html(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.text
