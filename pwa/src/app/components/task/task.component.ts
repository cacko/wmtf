import {
  Component,
  HostBinding,
  HostListener,
  Input,
  OnDestroy,
  OnInit,
} from '@angular/core';
import NgxFMG_ANIMATION from 'src/app/entity/animations';
import { TaskInfo } from 'src/app/entity/tasks.entity';

@Component({
  selector: 'app-task',
  templateUrl: './task.component.html',
  styleUrls: ['./task.component.scss'],
  animations: [NgxFMG_ANIMATION.TRIGGER_FADE_OUT],
})
export class TaskComponent implements OnInit, OnDestroy {
  private _remove: boolean = false;
  @Input() taskInfo!: TaskInfo;
  level: number | null = null;

  @HostBinding('@TRIGGER_FADE_OUT') get getLeaveDrawer(): boolean {
    return this._remove;
  }

  @HostListener('@TRIGGER_FADE_OUT.done') animationIsDone() {
    // if (this._remove) this.service.removeItem(this);
  }

  ngOnInit(): void {
    const level = this.taskInfo.estimate_used || 0;
    this.level =
      level < 100
        ? Math.ceil(this.toLevel(level) / 100) * 100
        : Math.ceil(this.toLevel(level - 100) / 100) * 100 * -1;
  }

  getProgressStyle() {
    const est_used = Math.min(this.taskInfo.estimate_used || 0, 100);
    return {
      width: `${est_used}%`,
    };
  }

  private toLevel(
    level: number,
    oldMax: number = 100,
    newMax: number = 900,
    newMin: number = 50
  ): number {
    return ((level - 0) * (newMax - newMin)) / (oldMax - 0) + newMin;
  }

  ngOnDestroy(): void {
    throw new Error('Method not implemented.');
  }
}
