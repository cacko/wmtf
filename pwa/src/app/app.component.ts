import { Component, OnInit } from '@angular/core';
import { ApiService } from './service/api.service';
import { NGXLogger } from 'ngx-logger';
import { WSCommand, WSRequest, WSType } from './entity/websockets.entity';
import { v4 as uuidv4 } from 'uuid';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  title = 'pwa';

  constructor(private ws: ApiService, private log: NGXLogger) {
    this.ws.connected.subscribe(() => {
      const msg: WSRequest = {
        ztype: WSType.REQUEST,
        client: this.ws.DEVICE_ID,
        id: uuidv4(),
        data: { cmd: WSCommand.TASKS },
      };
      this.ws.send(msg);
    });
    this.ws.responses.subscribe((res) => {
      log.info(res);
    });
  }
  ngOnInit(): void {
    this.ws.connect();
  }
}
