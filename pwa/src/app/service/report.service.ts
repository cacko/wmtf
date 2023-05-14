import { Injectable, inject } from '@angular/core';
import { ApiService } from './api.service';
import { WSCommand, WSResponse } from '../entity/websockets.entity';
import {
  ActivatedRouteSnapshot,
  ResolveFn,
  RouterStateSnapshot,
} from '@angular/router';
import { filter, map, tap } from 'rxjs';
import { ReportDay, WReportDay } from '../entity/report.entity';
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
        data.data.data?.result.map((d: WReportDay) => new ReportDay(d))
      ),
      tap((data: ReportDay[]) => {
        this.report = data;
        this.today = find(data, (d: ReportDay) => d.isToday);
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
