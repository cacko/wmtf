import { Component, OnInit } from '@angular/core';
import { ApiService } from './service/api.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  title = 'pwa';
  loading = true;
  updating = false;
  constructor(private ws: ApiService, private router: Router) {
    this.ws.showLoader();
    this.ws.connect();
    this.ws.connected.subscribe(() => {
      this.router.navigateByUrl('/dashboard');
    });
  }
  ngOnInit(): void {}
}
