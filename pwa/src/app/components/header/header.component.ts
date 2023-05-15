import { Component, Input, OnInit } from '@angular/core';
import { random, find } from 'lodash-es';
import * as moment from 'moment';
import { NGXLogger } from 'ngx-logger';
import { Observable, Subject, interval } from 'rxjs';
import { ReportDay, ReportTask } from 'src/app/entity/report.entity';
import { TaskInfo } from 'src/app/entity/tasks.entity';
import { User } from 'src/app/entity/user.entity';
import { ApiService } from 'src/app/service/api.service';
import { ReportService } from 'src/app/service/report.service';
import { TasksService } from 'src/app/service/tasks.service';
import { UserService } from 'src/app/service/user.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
})
export class HeaderComponent implements OnInit {
  public user?: User;
  public today?: ReportDay;
  public activeTask: TaskInfo | null = null;
  public taskStart: moment.Moment | null = null;

  public level = 0;
  public progress = 0;
  private todayWorkSubject = new Subject<moment.Duration>();
  todayWork$ = this.todayWorkSubject.asObservable();

  constructor(
    private userService: UserService,
    private logger: NGXLogger,
    private api: ApiService,
    private reportService: ReportService,
    private tasksService: TasksService
  ) { }

  ngOnInit(): void {
    this.userService.user.subscribe((user) => {
      if (user) {
        this.user = user;
      } else {
        delete this.user;
      }
    });
    this.tasksService.activeTask.subscribe((task: TaskInfo | null) => {
      this.activeTask = task;
      this.taskStart = this.activeTask?.clock_start || null;
      interval(30000).subscribe(() => {
        const today_work = this.today?.total_work || moment.duration({ seconds: 0 });
        this.todayWorkSubject.next(today_work);
        this.progress = Math.ceil((today_work.asSeconds() / (8 * 60 * 60)) * 100);
        this.level = ((this.progress - 0) * (900 - 50)) / (100 - 0) + 50;
        console.log(this.progress, today_work.asSeconds())
      });
    });

    this.api.connected.subscribe(() => {
      this.reportService.getReport().subscribe((data: any) => {
        this.today = this.reportService.today;
      });
    });
  }

  getProgressStyle() {
    return {
      width: `${this.progress}%`,
    };
  }

  fromDate(m: moment.Moment): string {
    const diff = moment.duration(moment().diff(m));
    const hours = diff.hours();
    const minutes = `${diff.minutes()}`.padStart(2, '0');
    return `${hours}:${minutes}`;
  }

}
