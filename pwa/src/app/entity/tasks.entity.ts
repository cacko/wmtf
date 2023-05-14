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
  group?: string;
}

export class TaskInfo {
  id!: number;
  summary!: string;
  clock_id!: number;
  clock!: ClockLocation;
  clock_start?: Moment | null;
  estimate?: Duration | null;
  estimate_used?: number | null;
  group?: string;

  constructor(api_info: WTaskInfoEntity) {
    Object.assign(this, api_info, {
      clock_start: moment(api_info.clock_start) || null,
      estimate: moment.duration(api_info.estimate || 0),
      estimate_used: api_info.estimate_used,
    });
  }

  get isActive(): boolean {
    return [ClockLocation.HOME, ClockLocation.OFFICE].includes(this.clock);
  }
}
