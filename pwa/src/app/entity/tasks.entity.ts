import { Duration, Moment } from 'moment';
import { ClockLocation } from './clock.entity';
import * as moment from 'moment';

export interface WTaskInfoEntity {
  id: number;
  summary: string;
  clock_id: number;
  clock: ClockLocation;
  clock_start?: number | null;
  estimate?: string | null;
  estimate_used?: number | null;
  task_updated?: string | null;
  group?: string;
}

export class TaskInfo {
  id!: number;
  summary!: string;
  clock_id!: number;
  clock!: ClockLocation;
  clock_start?: Moment | null;
  estimate?: Duration | null;
  task_updated?: Duration | null;
  estimate_used?: number | null;
  group?: string;

  constructor(api_info: WTaskInfoEntity) {
    Object.assign(this, api_info, {
      clock_start: moment(api_info.clock_start) || null,
      estimate: moment.duration(api_info.estimate || 0),
      task_updated: moment.duration(api_info.task_updated)
    });
  }

  get isActive(): boolean {
    return [ClockLocation.HOME, ClockLocation.OFFICE].includes(this.clock);
  }
}
