import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { shuffle } from 'lodash-es';
import { NGXLogger } from 'ngx-logger';
import { Subscription, interval } from 'rxjs';
import { TaskInfo } from 'src/app/entity/tasks.entity';
import { ApiService } from 'src/app/service/api.service';
import { TasksService } from 'src/app/service/tasks.service';

interface RouteDataEntity {
  data?: TaskInfo[];
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  tasks: TaskInfo[] = [];
  refresher?: Subscription;

  constructor(
    private activatedRoute: ActivatedRoute,
    private logger: NGXLogger,
    private tasksService: TasksService,
    private api: ApiService
  ) {}

  ngOnInit(): void {
    this.activatedRoute.data.subscribe((data: RouteDataEntity) => {
      this.tasks = data.data as TaskInfo[];
      this.logger.debug(this.tasks, 'Tasks');
      this.api.hideLoader();
      this.refresher = interval(60*1000*5).subscribe(() => {
        this.tasksService.getTasks().subscribe((data: TaskInfo[]) => {
          this.tasks = data;
        })
      });
    });
  }
}
