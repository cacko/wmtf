import { Component, Input } from '@angular/core';
import { TaskInfoEntity } from 'src/app/entity/tasks.entity';

@Component({
  selector: 'app-tasklist',
  templateUrl: './tasklist.component.html',
  styleUrls: ['./tasklist.component.scss']
})
export class TasklistComponent {

  @Input() tasks: TaskInfoEntity[] = [];
}
