import { Duration, Moment } from 'moment';
import { ClockLocation } from './clock.entity';
import * as moment from 'moment';

export interface WReportTask {
  id: number;
  clock: ClockLocation;
  clock_time: string;
  clock_start: string;
  clock_end: string;
  summary: string;
}

export interface WReportDay {
  day: string;
  total_work: string;
  tasks: WReportTask[];
}

export class ReportTask {
  id!: number;
  clock!: ClockLocation;
  clock_time!: Duration;
  clock_start!: Moment;
  clock_end!: Moment;
  summary!: string;

  constructor(api_data: WReportTask) {
    Object.assign(this, api_data, {
      clock_time: moment.duration(api_data.clock_time),
      clock_start: moment(api_data.clock_start) || null,
      clock_end: moment(api_data.clock_end),
    });
  }

  get isActive(): boolean {
    return [ClockLocation.HOME, ClockLocation.OFFICE].includes(this.clock);
  }

}

export class ReportDay {
  day!: Moment;
  total_work!: Duration;
  tasks!: ReportTask[];

  constructor(api_data: WReportDay) {
    Object.assign(this, api_data, {
      day: moment(api_data.day),
      total_work: moment.duration(api_data.total_work),
      tasks: api_data.tasks.map((t) => new ReportTask(t)),
    });
  }

  get isToday(): boolean {
    return this.day.isSame(moment(), 'day');
  }
}
