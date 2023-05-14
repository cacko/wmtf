import { Injectable } from '@angular/core';
import {
  Auth,
  User,
  onAuthStateChanged,
  onIdTokenChanged,
} from '@angular/fire/auth';
import { Subject } from 'rxjs';
import { ApiService } from './api.service';

interface MyUser extends User {
  accessToken?: string;
}
@Injectable({
  providedIn: 'root',
})
export class UserService {
  private userSubject = new Subject<User | null>();
  user = this.userSubject.asObservable();

  constructor(auth: Auth, ws: ApiService) {
    onAuthStateChanged(auth, (user: MyUser | null) => {
      if (!user) {
        this.userSubject.next(null);
        return;
      }
      console.log(user);
      ws.login(user);
      this.userSubject.next(user);
      onIdTokenChanged(auth, (changedUser) => {
        if (changedUser) {
          const newUser = changedUser as MyUser;
          const currentUser = user as MyUser;
          if (newUser.accessToken !== currentUser.accessToken) {
            ws.login(newUser);
          }
        }
      });
    });
  }
}
