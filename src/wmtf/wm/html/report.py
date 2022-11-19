import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any, Generator, Iterable, Optional

from bs4 import PageElement, element
from wmtf.config import app_config
from wmtf.wm.models import ClockLocation, ReportDay, ReportTask

from wmtf.wm.html.parser import Parser, extract_id_from_a, strip_tags


class HtmlReportMeta(type):

    __instances: dict[str, Any] = {}
    _parsing: bool = False

    def __call__(cls, *args, **kwds):
        klass = cls.__name__
        if klass not in cls.__instances:
            cls.__instances[klass] = type.__call__(cls, *args, **kwds)
        return cls.__instances[klass]

    def can_parse(cls, row):
        if cls._parsing:
            return True
        match row:
            case element.Tag():
                match row.name:
                    case "h2":
                        cls._parsing = (
                            f"work details for: {app_config.wm_config.username}"
                            == row.get_text().strip().lower()
                        )
        return False

    def process(cls, rows: Iterable[PageElement]):
        for row in rows:
            try:
                cls().do_process(row)
            except StopIteration:
                if cls().is_valid():
                    yield cls().get_model()
                del cls.__instances[cls.__name__]

    @property
    def day(cls) -> ReportDay:
        return HtmlReportDay().get_model()


class HtmlReportTask(object, metaclass=HtmlReportMeta):

    __items: list[str]
    __id: int
    __clock: ClockLocation
    __worktime: timedelta
    __start: datetime
    __end: datetime
    __description: str
    __day: date

    __WORKTIME_RE = re.compile(r"([\d]{2}:[\d]{2}) hrs")
    __CLOCK_START_END_RE = re.compile(r"([\d]{2}:[\d]{2}) -> ([\d]{2}:[\d]{2})")
    __CLOCK_RE = re.compile(r"\[(home|office)\]", re.IGNORECASE)

    def __init__(self, *args, **kwargs):
        self.__day = __class__.day.day
        self.__items = []
        self.__id = 0
        self.__clock = ClockLocation.OFF
        self.__worktime = timedelta(seconds=0)
        self.__start = datetime.combine(self.__day, time(0, 0))
        self.__end = datetime.combine(self.__day, time(0, 0))
        self.__description = ""

    def is_valid(self):
        return self.__id > 0

    def do_process(self, row: PageElement):
        match row:
            case element.Tag():
                match row.name:
                    case "br":
                        raise StopIteration
                    case "a":
                        self.__id = extract_id_from_a(row)
                        self.__description = strip_tags(row.get_text().strip())
                    case "b":
                        if fnt := row.find("font", attrs={"color": "green"}):
                            self.__clock = ClockLocation(fnt.get_text().strip().lower())
            case element.NavigableString():
                txt = row.get_text().strip()
                if wtm := self.__WORKTIME_RE.search(txt):
                    h, m = list(map(int, wtm.group(1).split(":")))
                    self.__worktime = timedelta(hours=h, minutes=m)
                if wcm := self.__CLOCK_START_END_RE.search(txt):
                    h, m = list(map(int, wcm.group(1).split(":")))
                    self.__start = datetime.combine(self.__day, time(h, m))
                    h, m = list(map(int, wcm.group(2).split(":")))
                    self.__end = datetime.combine(self.__day, time(h, m))
                if clm := self.__CLOCK_RE.search(txt):
                    self.__clock = ClockLocation(clm.group(1).lower())

    @property
    def items(self) -> list[str]:
        return self.__items

    def __str__(self) -> str:
        return "".join(self.__items)

    def get_model(self):
        return ReportTask(
            id=self.__id,
            clock=self.__clock,
            clock_time=self.__worktime,
            clock_start=self.__start,
            clock_end=self.__end,
            summary=self.__description,
        )


class HtmlReportDay(object, metaclass=HtmlReportMeta):

    __tasks: list[ReportTask]
    __rows: list[PageElement]
    __date: date
    __work: timedelta
    __last_tag: str
    __DATE_MATCH = re.compile(r"([\d]{1,2}\/[\d]{1,2}\/[\d]{2})")
    __WORK_MATCH = re.compile(r"[\d]{2}:[\d]{2}")

    def __init__(self) -> None:
        self.__tasks = []
        self.__rows = []
        self.__last_tag = ""

    def is_valid(self):
        return self.__date is not None

    def get_model(self):
        return ReportDay(day=self.date, total_work=self.__work, tasks=self.tasks)

    def do_process(self, row: PageElement):
        if not __class__.can_parse(row):
            return
        match row:
            case element.Tag():
                match row.name:
                    case "font":
                        self.__process_date(row)
                    case "br":
                        if self.__last_tag == "br":
                            self.__tasks = list(HtmlReportTask.process(self.__rows))
                            raise StopIteration
                        else:
                            self.__rows.append(row)
                    case _:
                        self.__rows.append(row)
                self.__last_tag = row.name

            case element.NavigableString():
                self.__rows.append(row)

    def __process_date(self, row):
        row_text = row.get_text().strip()
        if dm := self.__DATE_MATCH.search(row_text):
            self.__date = datetime.strptime(dm.group(), "%d/%m/%y").date()
        if wm := self.__WORK_MATCH.search(row_text):
            hours, minutes = list(map(int, wm.group().split(":")))
            self.__work = timedelta(hours=hours, minutes=minutes)

    @property
    def tasks(self) -> list[ReportTask]:
        return self.__tasks

    @property
    def date(self) -> date:
        return self.__date

    @property
    def total_work(self) -> timedelta:
        return self.__work

    def __str__(self) -> str:
        tasks_list = "\n\t".join(map(str, self.tasks))
        return f"{self.date} {self.total_work}\n\t{tasks_list}"


class HtmlContainer:

    __children: Iterable[PageElement]

    def __init__(self, el: element.Tag) -> None:
        self.__children = el.children

    def days(self) -> Generator[ReportDay, None, None]:
        yield from HtmlReportDay.process(self.__children)


class Report(Parser):
    def parse(self) -> list[ReportDay]:
        return list(self.container.days())

    @property
    def container(self) -> HtmlContainer:
        tds = self.struct.select('td[align="left"]')
        for row in tds[0].children:
            match row:
                case element.Tag():
                    if row.name == "p":
                        return HtmlContainer(row)
        raise NotImplementedError


class ReportId(Parser):
    def parse(self) -> int:
        el = self.struct.find("input", {"id": "reportForm.itemId"})
        assert isinstance(el, element.Tag)
        return int(el.attrs.get("value", "0"))
