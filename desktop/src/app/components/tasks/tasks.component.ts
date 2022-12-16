import { Component, OnInit } from '@angular/core';
import { AnyAaaaRecord } from 'dns';
import { ApiService } from '../../core/services/api.service';
import { ApiType } from '../../entity/api';

@Component({
  selector: 'app-tasks',
  templateUrl: './tasks.component.html',
  styleUrls: ['./tasks.component.scss']
})
export class TasksComponent implements OnInit {

  constructor(
    private api: ApiService
  ) { }

  ngOnInit(): void {
    this.api.fetch(ApiType.TASKS).then((tasks: any) => {
      console.log(tasks);
    }).catch(err => {

    });
  }

}
