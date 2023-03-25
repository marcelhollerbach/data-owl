import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MaterialExampleModule } from '../material.module';
import { DataViewComponent } from './data-management/data-view.component';
import { WizardComponent } from './wizard/wizard.component';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule }   from '@angular/forms';
import { TraitManagementComponent } from './trait-management/trait-management.component';
import { NewTraitEntry } from './trait-management/modal/new-trait-entry';
import { DataEntryDisplayComponent } from './utils/data-entry-display/data-entry-display.component';
import { NewDataEntry } from './utils/data-entry-display/modal/new-data-entry';
import { SearchBarComponent } from './utils/search-bar/search-bar.component';

@NgModule({
  declarations: [
    AppComponent,
    DataViewComponent,
    NewDataEntry,
    NewTraitEntry,
    WizardComponent,
    TraitManagementComponent,
    DataEntryDisplayComponent,
    SearchBarComponent,
  ],
  imports: [
    ReactiveFormsModule,
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

