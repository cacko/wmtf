import { Component, OnInit } from '@angular/core';
import { ApiService } from './service/api.service';
import { WSLoading } from './entity/websockets.entity';
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
  connected = false;
  constructor(private ws: ApiService, private router: Router) {
    this.ws.showLoader();
    this.ws.connected.subscribe((res) => {
      this.connected = res;
      this.router.navigateByUrl('/dashboard');
    });
    // this.ws.loading.subscribe((res) => {
    //   setTimeout(() => {
    //     [WSLoading.BLOCKING_OFF, WSLoading.BLOCKING_ON].includes(res) &&
    //       (this.loading = WSLoading.BLOCKING_ON === res);
    //   });
    // });
  }
  ngOnInit(): void {}
}
