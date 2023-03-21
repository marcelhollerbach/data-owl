import { DataSource, CollectionViewer } from '@angular/cdk/collections';
import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Observable } from 'rxjs';
import { DataEntriesService, DataEntryExploration } from '../data-entries.service';
import { DataTraitClass, DataTraitManagementService } from '../data-trait-management.service';
import { DataClass, DataTraitService } from '../data-trait.service';
import { NewTraitEntry } from './modal/new-trait-entry';

@Component({
  selector: 'app-trait-management',
  templateUrl: './trait-management.component.html',
  styleUrls: ['./trait-management.component.scss']
})
export class TraitManagementComponent {
  dataSource: DataManagementExplorationDataSource;
  displayedColumns = ['Titel', 'Description'];

  constructor(public create_dialog: MatDialog, public detail_dialog: MatDialog, private data_trait_management_service: DataTraitManagementService) {
    this.dataSource = new DataManagementExplorationDataSource(this.data_trait_management_service);
  }
  refresh() {
    this.dataSource = new DataManagementExplorationDataSource(this.data_trait_management_service);
  }
  openSingleCreationDialog(): void {
    this.show_entry({ id: "", immutable: false })
  }
  show_entry(entry: any) {
    let version = entry["title"]
    let immutable = entry["immutable"]
    if (immutable == false) {
      this.create_dialog.open(NewTraitEntry, {
        data: {
          id: version
        }
      }).afterClosed().subscribe((id) => this.refresh())
    }
  }
}

class DataManagementExplorationDataSource extends DataSource<DataTraitClass> {
  constructor(private data_trait_management_service: DataTraitManagementService) {
    super();
  }
  connect(_collectionViewer: CollectionViewer): Observable<readonly DataTraitClass[]> {
    return this.data_trait_management_service.findAll()
  }

  disconnect(_collectionViewer: CollectionViewer): void { }
}