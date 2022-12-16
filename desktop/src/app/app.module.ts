import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule, HttpClient, HTTP_INTERCEPTORS } from '@angular/common/http';
import { CoreModule } from './core/core.module';
import { SharedModule } from './shared/shared.module';

import { AppRoutingModule } from './app-routing.module';

// NG Translate
import { TranslateModule, TranslateLoader } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';

import { HomeModule } from './home/home.module';
import { DetailModule } from './detail/detail.module';

import { AppComponent } from './app.component';


import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
// import { LoaderComponent } from './components/loader/loader.component';
import { ApiService } from './core/services/api.service'
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { LoaderComponent } from './components/loader/loader.component';
import { MatGridListModule } from '@angular/material/grid-list';
import { TasksComponent } from './components/tasks/tasks.component';
import { ReportComponent } from './components/report/report.component';
import { TaskComponent } from './components/task/task.component';

// AoT requires an exported function for factories
const httpLoaderFactory = (http: HttpClient): TranslateHttpLoader => new TranslateHttpLoader(http, './assets/i18n/', '.json');

const MaterialModules = [
  MatIconModule,
  MatProgressBarModule,
  MatInputModule,
  MatButtonModule,
  MatExpansionModule,
  MatTooltipModule,
  MatSnackBarModule,
  MatGridListModule,
];

@NgModule({
  declarations: [AppComponent, LoaderComponent, TasksComponent, ReportComponent, TaskComponent],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    CoreModule,
    SharedModule,
    HomeModule,
    DetailModule,
    AppRoutingModule,
    ...MaterialModules,
    TranslateModule.forRoot({
      loader: {
        provide: TranslateLoader,
        useFactory: httpLoaderFactory,
        deps: [HttpClient]
      }
    })
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: ApiService,
      multi: true,
    },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
