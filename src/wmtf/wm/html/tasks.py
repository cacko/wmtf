from typing import Optional

import pandas as pd

from wmtf.wm.models import Task as TaskItem
from wmtf.wm.models import TaskComment, TaskInfo

from wmtf.wm.html.parser import (
    Parser,
    extract_clock,
    extract_id_from_url,
    strip_tags,
    extract_clock_time,
    extract_comment_time
)


class TaskList(Parser):
    def parse(self) -> list[TaskInfo]:
        df = pd.read_html(
            self.struct.prettify(), match="<1>", attrs={"cellpadding": "4"}
        )[0]
        columns = df.iloc[0]
        dfd = pd.read_html(
            self.struct.prettify(),
            match="<1>",
            extract_links="all",
            attrs={"cellpadding": "4"},
            skiprows=[0],
        )[0]
        dfd.columns = columns
        return [
            TaskInfo(
                id=extract_id_from_url(r.iloc[0][1]),
                clock_id=extract_id_from_url(r["CLOCK"][1]),
                clock=extract_clock(r["CLOCK"][0]),
                summary=strip_tags(r["Summary"][0]),
                clock_start=extract_clock_time(r["CLOCK"][0]),
            )
            for _, r in dfd.iterrows()
        ]


class Task(Parser):
    def init(self):
        for br in self.struct("br"):
            br.replace_with("<br>")

    def parse(self) -> TaskItem:
        df = pd.read_html(
            str(self.struct),
            match="Sales Pipeline",
        )[2]
        df.columns = df.iloc[0]
        task_row = df.iloc[1]

        return TaskItem(
            id=self.id,
            summary=task_row["Summary"],
            description=task_row["Desc"].replace("<br>", "\n"),
            assignee=task_row["Assignee"],
            comments=self.__get_comments(),
            create=task_row["Create"],
            priority=task_row["Priority"],
            value=task_row["Bus. Value"],
            group=task_row['Group']
        )

    def __get_comments(self) -> Optional[list[TaskComment]]:
        try:
            df = pd.read_html(self.struct.prettify(), match="Comment")[3]
            df.columns = df.iloc[0]
            return [
                TaskComment(
                    author=r["Who"],
                    comment=r["Comment"].replace("<br>", "\n>"),
                    timestamp=extract_comment_time(r["Date"]),
                )
                for _, r in df.drop([0, 1]).iterrows()
            ]
        except IndexError:
            pass
