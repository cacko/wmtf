import { Component, Input, OnInit } from '@angular/core';
import * as md5 from 'md5';
import { User } from 'src/app/entity/user.entity';
const b64encode = window.btoa;

interface ImageStyle {
  [key: string]: string;
}

@Component({
  selector: 'app-avatar',
  templateUrl: './avatar.component.html',
  styleUrls: ['./avatar.component.scss'],
})
export class AvatarComponent {
  @Input() user: User | undefined;
  imageStyle: ImageStyle = {};
  size = 30;
}
