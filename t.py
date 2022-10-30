from bs4 import BeautifulSoup, element
from pathlib import Path
from pprint import pprint

f = Path(".") / "tasks.html"

with f.open("rb") as fp:
    bs = BeautifulSoup(fp, features="html.parser")
    rows = bs.select('tr[height="20"]')
    items = []
    for row in rows:
        item = []
        for td in row.children:
            match(type(td)):
                case element.Tag:
                    item.append(td)
        items.append(item)
    print(items[6])
