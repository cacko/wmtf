import re
from typing import Optional, Generator
from urllib.parse import parse_qs, urlparse
from datetime import datetime

from bs4 import BeautifulSoup, element
from urlextract import URLExtract
from corestring import truncate
from rich.markup import escape
from wmtf.wm.models import ClockLocation
from functools import reduce

CLOCK_PATTERN = re.compile(r".+\((\w+)\)", re.MULTILINE)
CLOCK_START_PATTERN = re.compile(
    r"([123]\d?)/(1[012]?)\s+([01]\d):([012345]\d)", re.MULTILINE
)
TAG_RE = re.compile(r"<[^>]+>")


def extract_id_from_a(el: element.Tag):
    if el.name != "a":
        raise ValueError
    url = urlparse(el.attrs.get("href", ""))
    query = url.query
    itemId = parse_qs(query).get("itemId", [])
    return int(itemId[0])


def extract_id_from_url(url: Optional[str]):
    if not url:
        return 0
    qs = urlparse(url).query
    itemId = parse_qs(qs).get("itemId", [])
    return int(itemId[0])


def extract_clock(txt: str) -> ClockLocation:
    if matches := CLOCK_PATTERN.match(txt):
        return ClockLocation(matches.group(1))
    return ClockLocation.OFF


def extract_clock_start(text: str) -> Optional[datetime]:
    if matches := CLOCK_START_PATTERN.search(text):
        day, month, hour, minute = map(int, matches.groups())
        return datetime(
            year=datetime.now().year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
        )
    return None


def get_links(s: str) -> Generator[str, None, None]:
    for url in URLExtract().gen_urls(s, with_schema_only=True):
        try:
            assert isinstance(url, str)
            yield url
        except AssertionError:
            pass


def markdown_links(s: str) -> str:
    return reduce(
        lambda r, url: r.replace(url, f"[{truncate(url, 50)}]({url})"), get_links(s), s
    )


def console_links(s: str) -> str:
    return reduce(
        lambda r, url: r.replace(url, f"[link={url}]{truncate(url, 50)}[/link]"),
        get_links(s),
        s,
    )


def textual_links(s: str, action) -> str:
    return reduce(
        lambda r, url: r.replace(
            url, f"[@click={action}('{url}')]{truncate(url, 50)}[/]"
        ),
        get_links(s),
        s,
    )


def strip_tags(txt: str) -> str:
    return TAG_RE.sub("", txt)


class ParserError(Exception):
    pass


class Parser(object):

    struct: BeautifulSoup
    __id: int

    def __init__(self, html: bytes, id: int = 0) -> None:
        self.struct = BeautifulSoup(html, features="html.parser")
        self.__id = id
        self.handle_error()
        self.init()

    def init(self):
        pass

    @property
    def id(self) -> int:
        return self.__id

    def handle_error(self):
        error = self.struct.select('font[color="red"][size="+2"]')
        if not len(error):
            return
        if error_msg := error[0].get_text().strip():
            
            raise ParserError(error_msg)

    def to_element(self, code: str):
        return BeautifulSoup(code, features="html.parser")
