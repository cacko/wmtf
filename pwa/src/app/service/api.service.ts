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
} from '../entity/websockets.entity';

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

  private loaderSubject = new Subject<WSLoading>();
  loading = this.loaderSubject.asObservable();

  private connectedSubject = new Subject<boolean>();
  connected = this.connectedSubject.asObservable();

  errorSubject = new Subject<string>();
  error = this.errorSubject.asObservable();

  private ws?: WebSocket;
  private pinger?: Subscription;
  private reconnector?: Subscription;
  private deviceId: string;
  private __user?: User;

  constructor(private logger: NGXLogger) {
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
    this.loaderSubject.next(WSLoading.BLOCKING_ON);
  }
  public hideLoader(): void {
    this.loaderSubject.next(WSLoading.BLOCKING_OFF);
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
    this.create(this.URL);
  }

  public disconnect() {
    this.ws?.close();
  }

  public send(data: any) {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      this.connect();
      this.connected
        .pipe(first())
        .subscribe((connected) => connected && this.send(data));
    } else {
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
    (async () => {
      this.send({
        ztype: WSType.REQUEST,
        id: uuidv4(),
        client: this.DEVICE_ID,
        data: {cmd: WSCommand.LOGIN}
      });
    })();
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
    this.ws.onopen = () => this.login();
    this.ws.onmessage = (msg) => {
      this.reconnectAfter = WSConnection.RECONNECT_START;
      const json = JSON.parse(msg.data) as WSResponse;
      if (json.ztype == WSType.PONG) {
        this.logger.debug('PONG', json);
      } else {
        this.logger.debug('IN', json);
        this.responseSubject.next(json);
        this.startPing();
      }
      this.loaderSubject.next(WSLoading.MESSAGE_OFF);
    };
    this.ws.onerror = (err) => {
      this.ws?.close();
      this.reconnectAfter = WSConnection.RECONNECT_START;
    };
    this.ws.onclose = () => {
      this.pinger?.unsubscribe();
      this.connectedSubject.next(false);
      this.startReconnector();
    };
    this.out = {
      error: (err: any) => {
        this.logger.debug(err);
      },
      complete: () => {
        this.loaderSubject.next(WSLoading.MESSAGE_OFF);
      },
      next: (data: Object) => {
        this.loaderSubject.next(WSLoading.MESSAGE_ON);
        if (this.ws?.readyState === WebSocket.OPEN) {
          const payload = data as WSRequest;
          // every([
          //   Object.assign({ ztype: '' }, payload).ztype != WSType.PING,
          //   Object.assign({ ztype: '' }, payload).data.cmd != WSCommand.LOGIN,
          // ]) && this.requestSubject.next(payload);
          this.ws.send(JSON.stringify(data));
        }
      },
    };
  }
}
