import { Component } from '@angular/core';
import { AngularFireAuth } from '@angular/fire/compat/auth';
import { ApiService } from 'src/app/service/api.service';
import firebase from 'firebase/compat/app';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent {
  constructor(
    public auth: AngularFireAuth,
    private ws: ApiService,
  ) {}
  login_google() {
    this.ws.showLoader();
    if (window.location.hostname == 'localhost') {
      this.auth
      .signInWithRedirect(new firebase.auth.GoogleAuthProvider());
    } else {
      this.auth
        .signInWithPopup(new firebase.auth.GoogleAuthProvider());
    }
  }
  logout() {
    this.auth.signOut();
  }
}
