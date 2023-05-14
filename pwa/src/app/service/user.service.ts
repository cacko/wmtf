import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { ApiService } from './api.service';
import { Router } from '@angular/router';
import { User } from '../entity/user.entity';

interface MyUser extends User {
  accessToken?: string;
}
@Injectable({
  providedIn: 'root',
})
export class UserService {
  private userSubject = new Subject<User | null>();
  user = this.userSubject.asObservable();

  constructor(
    ws: ApiService,
    router: Router
    ) {

  }
}
