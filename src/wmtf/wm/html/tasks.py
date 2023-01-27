from typing import Optional
import pandas as pd
import logging
from wmtf.wm.models import Task as TaskItem
from wmtf.wm.models import TaskComment, TaskInfo
import re

BOLD_TAGS = re.compile(r'<\/?b>')

from wmtf.wm.html.parser import (
    Parser,
    extract_clock,
    extract_id_from_url,
    strip_tags,
    extract_clock_time,
    extract_comment_time,
    extract_estimate,
    extract_estimate_used,
)


class TaskList(Parser):

    def clean(self, html: bytes):
        html = re.sub(BOLD_TAGS, "", html.decode()).encode()
        return super().clean(html)

    def parse(self) -> list[TaskInfo]:
        df_all = pd.read_html(
            self.struct.prettify(), match="<1>", attrs={"cellpadding": "4"}
        )
        df = df_all[0]
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
                estimate=extract_estimate(r["Work"]),
                estimate_used=extract_estimate_used(r["Work"]),
                group=r["Group"][0].strip("-"),
            )
            for _, r in dfd.iterrows()
        ]


class Task(Parser):
    def init(self):
        for br in self.struct("br"):
            br.replace_with("<br>")

    def clean(self, html: bytes):
        html = re.sub(BOLD_TAGS, "", html.decode()).encode()
        return super().clean(html)

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
            group=task_row["Group"].strip('-'),
            estimate=extract_estimate([task_row["Work"]]),
            estimate_used=extract_estimate_used([task_row["Work"]]),
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
