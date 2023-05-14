import { Injectable, inject } from '@angular/core';
import { ApiService } from './api.service';
import { WSCommand, WSResponse } from '../entity/websockets.entity';
import {
  ActivatedRouteSnapshot,
  ResolveFn,
  RouterStateSnapshot,
} from '@angular/router';
import { filter, map, tap } from 'rxjs';
import * as moment from 'moment';
import { ReportDay, WReportDay, WReportTask } from '../entity/report.entity';
import { find } from 'lodash-es';

@Injectable({
  providedIn: 'root',
})
export class ReportService {
  report: ReportDay[] = [];
  today?: ReportDay;

  constructor(private api: ApiService) {}

  getReport(): any {
    this.api.request({ cmd: WSCommand.REPORT });
    return this.api.responses.pipe(
      filter((data: WSResponse) => data.data.cmd == WSCommand.REPORT),
      map((data: WSResponse) =>
        data.data.data?.result.map((d: WReportDay) =>
          Object.assign(d, {
            total_work: moment.duration(d.total_work || 0),
            day: moment(d.day),
            tasks: d.tasks.map((t: WReportTask) =>
              Object.assign(t, {
                clock_time: moment.duration(t.clock_time),
                clock_start: moment(t.clock_start),
                clock_end: moment(t.clock_end),
              })
            ),
          })
        )
      ),
      tap((data: ReportDay[]) => {
        this.report = data;
        this.today = find(data, (d => d.day.isSame(moment(), 'day')));
        return data;
      })
    );
  }
}

export const tasksResolver: ResolveFn<ReportDay[]> = (
  route: ActivatedRouteSnapshot,
  state: RouterStateSnapshot
) => {
  return inject(ReportService).getReport();
};
