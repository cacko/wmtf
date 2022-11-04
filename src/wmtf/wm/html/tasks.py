from collections import namedtuple

from bs4 import element

from wmtf.wm.items.task import TaskInfo, Task

from .parser import Parser, extract_clock, extract_id_from_a, strip_tags

TaskRow = namedtuple(
    "TaskRow",
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
                items.append(TaskRow(*item))
            except TypeError:
                pass
        tasks: list[TaskInfo] = []
        for t in items:
            id = extract_id_from_a(t.id.find("a"))
            summary = strip_tags(t.summary.get_text(strip=True).replace("\n", ""))
            clock_id, clock = extract_clock(t.clock)
            tasks.append(TaskInfo(id=id, summary=summary, clock_id=clock_id, clock=clock))
        return tasks

class Task(Parser):
    def parse(self) -> Task:
        pass
