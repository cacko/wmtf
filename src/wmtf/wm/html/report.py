from pprint import pprint
from typing import Optional

import pandas as pd
from bs4 import element

from .parser import Parser, extract_clock, extract_id_from_a, strip_tags


class Report(Parser):

    def parse(self):
        df = pd.read_html(self.struct.prettify(), header=0)
        print(df[2].info())
    #     container = self.get_container()
    #     days = []
    #     day = None
    #     item = None
    #     items = []
    #     last_name = ""
    #     for row in container.children:
    #         match row:
    #             case element.Tag():
    #                 match row.name:
    #                     case 'font':
    #                         if not day:
    #                             day = row
    #                     case 'br':
    #                         if last_name == "br":
    #                             days.append((day, items[:]))
    #                             day = None
    #                             item = None
    #                             items = []
    #                         elif item:
    #                             items.append(item[:])
    #                             item = []
    #                     case _:
    #                         if day:                                
    #                             if not item:
    #                                 item = []
    #                             item.append(row)
    #                 last_name = row.name
                            
    #             case element.NavigableString():
    #                 if item:
    #                     item.append(row)
    #     pprint(days)
                
    # def get_container(self) -> element.Tag:
    #     tds = self.struct.select('td[align="left"]')
    #     for row in tds[0].children:
    #         match row:
    #             case element.Tag():
    #                 if row.name == "p":
    #                     return row
    #     raise NotImplementedError
