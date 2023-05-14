import { Component, Input, OnInit } from '@angular/core';
import { random } from 'lodash-es';
import { NGXLogger } from 'ngx-logger';
import { User } from 'src/app/entity/user.entity';
import { UserService } from 'src/app/service/user.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
})
export class HeaderComponent implements OnInit {
  user?: User;
  level = 500;

  constructor(
    private userService: UserService,
    private logger: NGXLogger
    ) {

  }

  ngOnInit(): void {
    this.userService.user.subscribe((user) => {
      if (user) {
        this.user = user;
        this.level =  Math.ceil(this.toLevel(random(0, 100)) / 100) * 100
      } else {
        delete this.user;
      }
    });
  }

  getProgressStyle() {
    const est_used = random(0, 100);
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
