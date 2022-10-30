from bs4 import BeautifulSoup, element
from pathlib import Path
from pprint import pprint
from collections import namedtuple
from urllib.parse import parse_qs, urlparse

def extract_id_from_a(el: element.Tag):
    if el.name != "a":
        raise ValueError
    url = urlparse(el.attrs.get("href", ""))
    query = url.query
    itemId = parse_qs(query).get("itemId", [])
    return int(itemId[0])


TaskRow = namedtuple('TaskRow', "id,clock,summary,parent,group,priority,assignee,jira,update,create,dealline,bus_value,sched,work,sales_task,sales_pipeline,open")

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
        try:
            items.append(TaskRow(*item))
        except TypeError:
            pass
    tasks = []
    for t in items:
        id = extract_id_from_a(t.id.find("a"))
        summary = t.summary.get_text(strip=True)
        print(id, summary)
