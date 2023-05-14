import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { APP_CONFIG } from '../environments/environment';
import { BrowserModule } from '@angular/platform-browser';
import { LoggerModule, NgxLoggerLevel } from 'ngx-logger';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HeaderComponent } from './components/header/header.component';
import { TaskComponent } from './components/task/task.component';
import { TasklistComponent } from './components/tasklist/tasklist.component';
import { AppRoutingModule } from './app-routing.module';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { PlatformModule } from '@angular/cdk/platform';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatRippleModule } from '@angular/material/core';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { OverlayModule } from '@angular/cdk/overlay';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatBottomSheetModule } from '@angular/material/bottom-sheet';
import { MatListModule } from '@angular/material/list';
import { TextFieldModule } from '@angular/cdk/text-field';
import { MomentModule } from 'ngx-moment';
import { AvatarComponent } from './components/avatar/avatar.component';
import { HttpClientModule } from '@angular/common/http';
import { AvatarModule } from 'ngx-avatars';
import { NgxSpinnerModule } from 'ngx-spinner';

const MaterialModules = [
  MatSelectModule,
  MatCardModule,
  MatSnackBarModule,
  MatDividerModule,
  MatProgressBarModule,
  MatButtonModule,
  MatIconModule,
  OverlayModule,
  MatAutocompleteModule,
  MatBottomSheetModule,
  MatListModule,
  TextFieldModule,
  PlatformModule,
  MatTooltipModule,
  MatRippleModule,
  DragDropModule,
  MatToolbarModule,
  MatSelectModule,
];

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    TaskComponent,
    TasklistComponent,
    DashboardComponent,
    AvatarComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ...MaterialModules,
    MomentModule,
    NgxSpinnerModule,
    AvatarModule,
    HttpClientModule,
    BrowserAnimationsModule,
    LoggerModule.forRoot({
      level: APP_CONFIG.production ? NgxLoggerLevel.INFO : NgxLoggerLevel.DEBUG,
    }),
  ],
  providers: [],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  bootstrap: [AppComponent],
})
export class AppModule {}
