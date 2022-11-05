import re
from typing import Optional
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup, element

from wmtf.wm.items.task import ClockLocation

CLOCK_PATTERN = re.compile(r".+\((\w+)\)", re.MULTILINE)
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


def strip_tags(txt: str) -> str:
    return TAG_RE.sub("", txt)


class Parser(object):

    struct: BeautifulSoup
    __id: int

    def __init__(self, html: bytes, id: int = 0) -> None:
        self.struct = BeautifulSoup(html, features="html.parser")
        self.__id = id
        self.init()

    def init(self):
        pass

    @property
    def id(self) -> int:
        return self.__id

    def to_element(self, code: str):
        return BeautifulSoup(code, features="html.parser")
