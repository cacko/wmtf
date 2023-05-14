import { Injectable } from '@angular/core';
import { NGXLogger } from 'ngx-logger';
import {
  first,
  Observable,
  Observer,
  timer,
  interval,
  Subscription,
} from 'rxjs';
import { Subject } from 'rxjs';
import { v4 as uuidv4 } from 'uuid';
import {
  WSConnection,
  WSRequest,
  WSResponse,
  WSPing,
  WSType,
  WSLoading,
  WSCommand,
  Payload,
} from '../entity/websockets.entity';
import { NgxSpinnerService } from 'ngx-spinner';
import { User } from '../entity/user.entity';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private out: Observer<MessageEvent<any>> | undefined;
  private in: Observable<MessageEvent<any>> | undefined;

  private reconnectAfter = 0;

  private responseSubject = new Subject<WSResponse>();
  responses = this.responseSubject.asObservable();

  private requestSubject = new Subject<WSRequest>();
  requests = this.requestSubject.asObservable();

  private wsConnectedSubject = new Subject<boolean>();
  private wsConnected = this.wsConnectedSubject.asObservable();

  private connectedSubject = new Subject<User>();
  connected = this.connectedSubject.asObservable();

  errorSubject = new Subject<string>();
  error = this.errorSubject.asObservable();

  private ws?: WebSocket;
  private pinger?: Subscription;
  private reconnector?: Subscription;
  private deviceId: string;
  private __user?: User;

  constructor(
    private logger: NGXLogger,
    private spinnerService: NgxSpinnerService
  ) {
    let id = localStorage.getItem('device_id');
    if (!id) {
      id = uuidv4();
      localStorage.setItem('device_id', id);
    }
    if (localStorage.getItem(`${id}_LOCKED`)) {
      id = uuidv4();
    }
    localStorage.setItem(`${id}_LOCKED`, '1');
    this.deviceId = id;
  }

  public showLoader(): void {
    this.spinnerService.show();
  }
  public hideLoader(): void {
    this.spinnerService.hide();
  }

  get URL(): string {
    return `${WSConnection.WS_URL}/${this.DEVICE_ID}`;
  }

  get DEVICE_ID(): string {
    return this.deviceId;
  }

  get USER(): User {
    if (!this.__user) {
      throw Error('not logged in');
    }
    return this.__user;
  }

  set USER(user: User) {
    this.__user = user;
  }

  public unlock() {
    localStorage.removeItem(`${this.DEVICE_ID}_LOCKED`);
  }

  public connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.wsConnectedSubject.next(true);
    } else {
      this.create(this.URL);
    }
  }

  public disconnect() {
    this.ws?.close();
  }

  public request(payload: Payload) {
    const rq: WSRequest = {
      ztype: WSType.REQUEST,
      client: this.DEVICE_ID,
      id: uuidv4(),
      data: payload,
    };
    this.logger.debug(rq);
    this.send(rq);
  }

  public send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.out?.next(data);
    }
  }

  public reconnect() {
    this.stopPing();
    timer(3000).subscribe(() => {
      try {
        this.create(`${this.URL}`);
        this.logger.debug('Successfully REconnected: ' + this.URL);
      } catch (err) {
        this.logger.error('Reconnect error', err);
        this.startPing();
      }
    });
  }

  private startPing() {
    this.stopPing();
    this.pinger = interval(20000).subscribe(() => {
      const ping: WSPing = {
        ztype: WSType.PING,
        id: uuidv4(),
        client: this.DEVICE_ID,
      };
      this.send(ping);
    });
  }

  private stopPing() {
    this.pinger?.unsubscribe();
  }

  public login() {
    this.send({
      ztype: WSType.LOGIN,
      id: uuidv4(),
      client: this.DEVICE_ID,
      data: {
        cmd: WSCommand.LOGIN,
      },
    });
  }

  private startReconnector() {
    if (this.stopReconnector()) {
      this.reconnector = timer(this.reconnectAfter).subscribe(() => {
        this.reconnect();
        this.reconnectAfter += this.reconnectAfter * 0.1;
      });
    }
  }

  private stopReconnector(): boolean {
    if (this.reconnector?.closed) {
      return false;
    }
    this.reconnector?.unsubscribe();
    delete this.reconnector;

    return true;
  }

  private create(url: string | URL): void {
    try {
      this.pinger?.unsubscribe();
    } catch (err) {}
    this.ws = new WebSocket(url);
    this.ws.onopen = () => {
      this.wsConnectedSubject.next(true);
      this.stopReconnector();
      this.reconnectAfter = WSConnection.RECONNECT_START;
      this.login();
    };
    this.ws.onmessage = (msg) => {
      this.reconnectAfter = WSConnection.RECONNECT_START;
      const data = JSON.parse(msg.data) as WSResponse;
      this.logger.info(data, 'onmessage');
      switch (data.ztype) {
        case WSType.PONG:
          this.logger.debug('PONG', data);
          break;
        case WSType.LOGIN:
          this.logger.debug('IN', data);
          this.connectedSubject.next(data.data.data?.result as User);
          this.startPing();
          break;
        case WSType.RESPONSE:
          this.responseSubject.next(data);
      }
    };
    this.ws.onerror = (err) => {
      this.ws?.close();
    };
    this.ws.onclose = () => {
      this.pinger?.unsubscribe();
      this.wsConnectedSubject.next(false);
      // this.startReconnector();
    };
    this.out = {
      error: (err: any) => {
        this.logger.error(err);
      },
      complete: () => {},
      next: (data: Object) => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.logger.debug(data, 'out');
          this.ws.send(JSON.stringify(data));
        }
      },
    };
  }
}
