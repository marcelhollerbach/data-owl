import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MaterialExampleModule } from '../material.module';
import { DataViewComponent } from './data-management/data-view.component';
import { NewDataEntry } from "./data-management/modal/new-data-entry";
import { WizardComponent } from './wizard/wizard.component';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule }   from '@angular/forms';
import { TraitManagementComponent } from './trait-management/trait-management.component';
import { NewTraitEntry } from './trait-management/modal/new-trait-entry';

@NgModule({
  declarations: [
    AppComponent,
    DataViewComponent,
    NewDataEntry,
    NewTraitEntry,
    WizardComponent,
    TraitManagementComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    MaterialExampleModule,
    HttpClientModule,
    BrowserAnimationsModule,
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }

