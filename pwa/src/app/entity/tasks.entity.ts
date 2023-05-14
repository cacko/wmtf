


export interface TaskInfoEntity {
  id: number;
  summary: string;
  clock_id: number;
  clock: string;
  clock_start?: number|null;
  estimate?: string|null;
  estimate_used?: number|null;
  group?:string;
}
