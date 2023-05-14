import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NGXLogger } from 'ngx-logger';
import { TaskInfoEntity } from 'src/app/entity/tasks.entity';

interface RouteDataEntity {
  data?: TaskInfoEntity[];
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  tasks: TaskInfoEntity[] = [];

  constructor(
    private activatedRoute: ActivatedRoute,
    private logger: NGXLogger
  ) {}

  ngOnInit(): void {
    this.activatedRoute.data.subscribe((data: RouteDataEntity) => {
      this.tasks = data.data as TaskInfoEntity[];
      this.logger.debug(this.tasks);
    });
  }
}
