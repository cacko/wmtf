import { Component, Input, OnInit } from '@angular/core';
import { random, find } from 'lodash-es';
import * as moment from 'moment';
import { NGXLogger } from 'ngx-logger';
import { ReportDay, ReportTask } from 'src/app/entity/report.entity';
import { User } from 'src/app/entity/user.entity';
import { ApiService } from 'src/app/service/api.service';
import { ReportService } from 'src/app/service/report.service';
import { UserService } from 'src/app/service/user.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
})
export class HeaderComponent implements OnInit {
  public user?: User;
  public level = 500;
  public today?: ReportDay;
  public activeTask?: ReportTask;
  public taskStart?: moment.Moment;

  constructor(
    private userService: UserService,
    private logger: NGXLogger,
    private api: ApiService,
    private reportService: ReportService
  ) {}

  ngOnInit(): void {
    this.userService.user.subscribe((user) => {
      if (user) {
        this.user = user;
        this.level = Math.ceil(this.toLevel(random(0, 100)) / 100) * 100;
      } else {
        delete this.user;
      }
    });
    this.api.connected.subscribe(() => {
      this.reportService.getReport().subscribe((data: any) => {
        console.log(data);
        this.today = this.reportService.today;
        this.activeTask = find(this.today?.tasks, (t) => t.isActive);
        console.log(this.activeTask);
        this.taskStart = this.activeTask?.clock_start;
      });
    });
  }

  getProgressStyle() {
    const est_used = random(0, 100);
    return {
      width: `${est_used}%`,
    };
  }

  fromDate(m: moment.Moment): string {
    const diff = moment.duration(moment().diff(m));
    const hours = diff.hours();
    const minutes = `${diff.minutes()}`.padStart(2, '0');
    return `${hours}:${minutes}`;
  }

  private toLevel(
    level: number,
    oldMax: number = 100,
    newMax: number = 900,
    newMin: number = 50
  ): number {
    return ((level - 0) * (newMax - newMin)) / (oldMax - 0) + newMin;
  }
}
