import { Component, OnInit } from '@angular/core';
import { ApiService } from './service/api.service';
import { NGXLogger } from 'ngx-logger';
import { WSLoading } from './entity/websockets.entity';
import { UserService } from './service/user.service';
import { SwUpdate, VersionEvent } from '@angular/service-worker';
import { MatSnackBar } from '@angular/material/snack-bar';
import { interval } from 'rxjs';
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
  constructor(
    private ws: ApiService,
    private user: UserService,
    private log: NGXLogger,
    private snackBar: MatSnackBar,
    private swUpdate: SwUpdate,
    private router: Router
  ) {
    this.ws.showLoader();
    if (this.swUpdate.isEnabled) {
      this.swUpdate.versionUpdates.subscribe((evt: VersionEvent) => {
        if (evt.type == 'VERSION_READY') {
          this.updating = true;
          this.snackBar
            .open('Update is available', 'Update')
            .onAction()
            .subscribe(() =>
              this.swUpdate
                .activateUpdate()
                .then(() => document.location.reload())
            );
        }
      });
      interval(10000).subscribe(() => {
        this.swUpdate.checkForUpdate();
      });
    }
    this.ws.connected.subscribe((res) => {
      this.connected = res;
    });
    this.ws.loading.subscribe((res) => {
      setTimeout(() => {
        [WSLoading.BLOCKING_OFF, WSLoading.BLOCKING_ON].includes(res) &&
          (this.loading = WSLoading.BLOCKING_ON === res);
      });
    });
  }
  ngOnInit(): void {
  }
}
