from bs4 import element
from urllib.parse import parse_qs, urlparse

def extract_id_from_a(el: element.Tag):
    if el.name != "a":
        raise ValueError
    url = urlparse(el.attrs.get("href", ""))
    query = url.query
    itemId = parse_qs(query).get("itemId", [])
    return int(itemId[0])
