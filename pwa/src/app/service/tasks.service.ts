import { Injectable, inject } from '@angular/core';
import {
  ActivatedRouteSnapshot,
  ResolveFn,
  RouterStateSnapshot,
} from '@angular/router';
import { TaskInfoEntity } from '../entity/tasks.entity';
import { ApiService } from './api.service';
import { WSCommand, WSResponse } from '../entity/websockets.entity';
import { filter, map } from 'rxjs';
import * as moment from 'moment';

@Injectable({
  providedIn: 'root',
})
export class TasksService {
  constructor(private api: ApiService) {}

  getTasks(): any {
    this.api.connected.subscribe(() => {
      this.api.request({ cmd: WSCommand.TASKS });
    });
    return this.api.responses.pipe(
      filter((data: WSResponse) => data.data.cmd == WSCommand.TASKS),
      map((data: WSResponse) =>
        data.data.data?.result.map((t: TaskInfoEntity) =>
          Object.assign(t, { estimate: moment.duration(t.estimate || 0).asSeconds() })
        )
      )
    );
  }
}

export const tasksResolver: ResolveFn<TaskInfoEntity[]> = (
  route: ActivatedRouteSnapshot,
  state: RouterStateSnapshot
) => {
  return inject(TasksService).getTasks();
};
