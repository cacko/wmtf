import { Component, Input, OnInit } from '@angular/core';
import { random } from 'lodash-es';
import { TaskInfoEntity } from 'src/app/entity/tasks.entity';

@Component({
  selector: 'app-task',
  templateUrl: './task.component.html',
  styleUrls: ['./task.component.scss'],
})
export class TaskComponent implements OnInit {
  @Input() taskInfo!: TaskInfoEntity;
  level: number | null = null;


  ngOnInit(): void {
    const level = this.taskInfo.estimate_used || 0;
    this.level =
      level < 100
        ? Math.ceil(this.toLevel(level) / 100) * 100
        : Math.ceil(this.toLevel(level - 100) / 100) * 100 * -1;
  }

  getProgressStyle() {
    const est_used = Math.min((this.taskInfo.estimate_used ||0), 100);
    return {
      width: `${est_used}%`
    }
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
