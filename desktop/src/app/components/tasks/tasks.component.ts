import { Component, OnInit } from '@angular/core';
import { AnyAaaaRecord } from 'dns';
import { ApiService } from '../../core/services/api.service';
import { ApiType } from '../../entity/api';
import { TaskInfo } from '../../entity/task';

@Component({
  selector: 'app-tasks',
  templateUrl: './tasks.component.html',
  styleUrls: ['./tasks.component.scss']
})
export class TasksComponent implements OnInit {

  items: TaskInfo[] = [];
  selected: TaskInfo[] = null;

  constructor(
    private api: ApiService
  ) { }

  ngOnInit(): void {
    this.api.fetch(ApiType.TASKS).then((tasks: TaskInfo[]) => {
      this.items = tasks;
    }).catch(err => {

    });
  }

  openTask(task: TaskInfo) {
    console.log(task);
  }

}
