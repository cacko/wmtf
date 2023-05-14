import { Duration, Moment } from "moment";

export interface WTaskInfoEntity {
  id: number;
  summary: string;
  clock_id: number;
  clock: string;
  clock_start?: number | null;
  estimate?: string | null;
  estimate_used?: number | null;
  group?: string;
}

export interface TaskInfoEntity {
  id: number;
  summary: string;
  clock_id: number;
  clock: string;
  clock_start?: Moment | null;
  estimate?: Duration | null;
  estimate_used?: number | null;
  group?: string;
}
