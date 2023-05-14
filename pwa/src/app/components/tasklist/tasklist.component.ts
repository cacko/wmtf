import { Component, Input } from '@angular/core';
import { findIndex } from 'lodash-es';
import { TaskInfo } from 'src/app/entity/tasks.entity';

@Component({
  selector: 'app-tasklist',
  templateUrl: './tasklist.component.html',
  styleUrls: ['./tasklist.component.scss'],
})
export class TasklistComponent {
  items: TaskInfo[] = [];

  @Input() set tasks(items: TaskInfo[]) {
    const newIds = items.map((t) => t.id);
    this.items
      .filter((d) => !newIds.includes(d.id))
      .forEach((t) =>
        this.items.splice(findIndex(this.items, { id: t.id }), 1)
      );
    const ids = this.items.map((t) => t.id);
    items
      .filter((d) => !ids.includes(d.id))
      .forEach((t) => this.items.splice(findIndex(items, { id: t.id }), 0, t));
    this.items.sort((a, b) => {
      const ax = findIndex(items, { id: a.id });
      const bx = findIndex(items, { id: b.id });
      return ax > bx ? 1 : -1;
    });
  }
}
