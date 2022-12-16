import { Injectable } from '@angular/core';
import {
  HttpClient,
  HttpErrorResponse,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  HttpResponse,
} from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { ActivatedRouteSnapshot, Params } from '@angular/router';
import { ApiType } from '../../entity/api'
import { isEmpty, omitBy } from 'lodash-es';


export interface LoaderState {
  show: boolean;
}

export enum Sort {
  ASC = 'asc',
  DESC = 'desc',
}

@Injectable({
  providedIn: 'root',
})
export class ApiService implements HttpInterceptor {
  static readonly API_MENU = '';
  static readonly CACHE_MINUTES = 5;

  public loading = false;

  private loaderSubject = new Subject<LoaderState>();
  loaderState = this.loaderSubject.asObservable();

  errorSubject = new Subject<string>();
  error = this.errorSubject.asObservable();

  constructor(private httpClient: HttpClient) { }

  intercept(
    req: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    this.showLoader();
    return next.handle(req).pipe(
      tap(
        (event: HttpEvent<any>) => {
          if (event instanceof HttpResponse) {
            this.onEnd();
          }
        },
        (err: HttpErrorResponse) => {
          this.onEnd();
          this.errorSubject.next(err.message);
        }
      )
    );
  }
  private onEnd(): void {
    this.hideLoader();
  }
  public showLoader(): void {
    this.loaderSubject.next(<LoaderState>{ show: true });
  }
  public hideLoader(): void {
    this.loaderSubject.next(<LoaderState>{ show: false });
  }

  fetch(path: string, params: Params = {}): Promise<any> {
    return new Promise((resolve, reject) => {
      this.httpClient
        .get(`http://localhost:44331/${path}`, {
          params: omitBy(params, isEmpty),
        })
        .subscribe({
          next: (data) => {
            return resolve(data);
          },
          error: (error) => {
            return reject(error);
          },
        });
    });
  }
}
