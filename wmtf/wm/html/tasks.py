from .parser import Parser, extract_clock, extract_id_from_a
from wmtf.wm.items.task import Task
from collections import namedtuple
from bs4 import element

TaskRow = namedtuple('TaskRow', "id,clock,summary,parent,group,priority,assignee,jira,update,create,dealline,bus_value,sched,work,sales_task,sales_pipeline,open")


class Tasks(Parser):

    def parse(self):
        rows = self.struct.select('tr[height="20"]')
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
        tasks: list[Task] = []
        for t in items:
            id = extract_id_from_a(t.id.find("a"))
            summary = t.summary.get_text(strip=True)
            clock_id, clock = extract_clock(t.clock)
            tasks.append(Task(
                id=id,
                summary=summary,
                clock_id=clock_id,
                clock=clock
            ))
        return tasks
