import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DataViewComponent } from './data-management/data-view.component';
import { TraitManagementComponent } from './trait-management/trait-management.component';
import { WizardComponent } from './wizard/wizard.component';

const routes: Routes = [
  { path: 'dataEntries', component: DataViewComponent },
  { path: 'traitManagement', component: TraitManagementComponent },
  { path: '**', component: WizardComponent },  
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
