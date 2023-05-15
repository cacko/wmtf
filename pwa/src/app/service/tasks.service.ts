import { Injectable, inject } from '@angular/core';
import {
  ActivatedRouteSnapshot,
  ResolveFn,
  RouterStateSnapshot,
} from '@angular/router';
import { WTaskInfoEntity, TaskInfo } from '../entity/tasks.entity';
import { ApiService } from './api.service';
import { WSCommand, WSResponse } from '../entity/websockets.entity';
import { Subject, filter, map, tap } from 'rxjs';
import { find } from 'lodash-es';


@Injectable({
  providedIn: 'root',
})
export class TasksService {
  constructor(private api: ApiService) { }

  private activeTaskSubject = new Subject<TaskInfo | null>();
  activeTask = this.activeTaskSubject.asObservable();

  getTasks(): any {
    this.api.request({ cmd: WSCommand.TASKS });
    return this.api.responses.pipe(
      filter((data: WSResponse) => data.data.cmd == WSCommand.TASKS),
      map((data: WSResponse) =>
        data.data.data?.result.map((t: WTaskInfoEntity) => (new TaskInfo(t)))
      ),
      tap(
        (tasks: TaskInfo[]) => {
          const active = find(tasks, (t) => t.isActive) || null;
          this.activeTaskSubject.next(active);
        }));
  }

}

export const tasksResolver: ResolveFn<TaskInfo[]> = (
  route: ActivatedRouteSnapshot,
  state: RouterStateSnapshot
) => {
  return inject(TasksService).getTasks();
};
