export interface TaskInfo {
  id: number;
  clock_id: number;
  clock: string;
  clock_start?: number;
  estimate?: number;
  estimate_user?: number;
  summary: string;
}
