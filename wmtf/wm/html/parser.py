from bs4 import element, BeautifulSoup
from urllib.parse import parse_qs, urlparse
from wmtf.wm.items.task import ClockLocation
import re

CLOCK_PATTERN = re.compile(r".+\((\w+)\)", re.MULTILINE)

def extract_id_from_a(el: element.Tag):
    if el.name != "a":
        raise ValueError
    url = urlparse(el.attrs.get("href", ""))
    query = url.query
    itemId = parse_qs(query).get("itemId", [])
    return int(itemId[0])

def extract_clock(el: element.Tag) -> tuple[int, ClockLocation]:
    links = el.find_all("a")
    id = extract_id_from_a(links[0])
    if len(links) == 2:
        return (id, ClockLocation.OFF)
    if matches := CLOCK_PATTERN.match(links[0].get_text()):
        return (id, ClockLocation(matches.group(1)))
    return (id, ClockLocation.OFF)

class Parser(object):

    struct: BeautifulSoup

    def __init__(self, html: bytes) -> None:
        self.struct = BeautifulSoup(html, features="html.parser")
