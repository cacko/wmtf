from collections import namedtuple
from typing import Optional

import pandas as pd
from bs4 import element

from wmtf.wm.items.task import Task as TaskItem
from wmtf.wm.items.task import TaskComment, TaskInfo

from .parser import Parser, extract_clock, extract_id_from_a, strip_tags

TaskInfoRow = namedtuple(
    "TaskInfoRow",
    "id,clock,summary,parent,group,priority,assignee,jira,update,create,dealline,bus_value,sched,work,sales_task,sales_pipeline,open",
)


class Tasks(Parser):
    def parse(self) -> list[TaskInfo]:
        rows = self.struct.select('tr[height="20"]')
        items = []
        for row in rows:
            item = []
            for td in row.children:
                match (type(td)):
                    case element.Tag:
                        item.append(td)
            try:
                items.append(TaskInfoRow(*item))
            except TypeError:
                pass
        tasks: list[TaskInfo] = []
        for t in items:
            id = extract_id_from_a(t.id.find("a"))
            summary = strip_tags(t.summary.get_text(strip=True).replace("\n", ""))
            clock_id, clock = extract_clock(t.clock)
            tasks.append(
                TaskInfo(id=id, summary=summary, clock_id=clock_id, clock=clock)
            )
        return tasks


class Task(Parser):
    def init(self):
        for br in self.struct("br"):
            br.replace_with("<br>")

    def parse(self) -> TaskItem:
        df = pd.read_html(self.struct.prettify(), match="Sales Pipeline")[2]
        df.columns = df.iloc[0]
        task_row = df.iloc[1]
        return TaskItem(
            id=self.id,
            summary=task_row["Summary"],
            description=task_row["Desc"].replace("<br>", "\n\n"),
            assignee=task_row["Assignee"],
            comments=self.__get_comments(),
        )

    def __get_comments(self) -> Optional[list[TaskComment]]:
        df = pd.read_html(self.struct.prettify(), match="Comment")[3]
        df.columns = df.iloc[0]
        result = []
        for _, r in df.drop([0,1]).iterrows():
            result.append(TaskComment(
                author=r["Who"],
                comment=r["Comment"].replace("<br>", "\n>"),
                date=r["Date"]
            ))
        return result
