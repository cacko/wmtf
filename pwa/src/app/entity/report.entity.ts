import { Duration, Moment } from "moment";


export interface WReportTask {
  id: number;
  clock: string;
  clock_time: string;
  clock_start: string;
  clock_end: string;
  summary: string;
}

export interface ReportTask {
  id: number;
  clock: string;
  clock_time: Duration;
  clock_start: Moment;
  clock_end: Moment;
  summary: string;
}

export interface WReportDay {
  day: string;
  total_work: string;
  tasks: WReportTask[];
}

export interface ReportDay {
  day: Moment;
  total_work: Duration;
  tasks: ReportTask[];
}

