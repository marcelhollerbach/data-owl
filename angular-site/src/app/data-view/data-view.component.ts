import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Observable } from 'rxjs';
import { DataEntriesService, DataEntryExploration } from '../data-entries.service';
import { DataSource } from '@angular/cdk/table';
import { CollectionViewer } from '@angular/cdk/collections';
import { NewDataEntry } from './modal/new-data-entry';


@Component({
  selector: 'app-data-view',
  templateUrl: './data-view.component.html',
  styleUrls: ['./data-view.component.scss']
})
export class DataViewComponent {
  dataSource : DataEntryExplorationDataSource;
  displayedColumns = ['Name', 'Description'];

  constructor(public create_dialog: MatDialog, public detail_dialog: MatDialog, private data_entry_service: DataEntriesService) {
    this.dataSource = new DataEntryExplorationDataSource(this.data_entry_service);
  }
  refresh() {
    this.dataSource = new DataEntryExplorationDataSource(this.data_entry_service);
  }
  openSingleCreationDialog(): void {
    this.show_entry({ id: "" })
  }
  show_entry(entry: any) {
    this.create_dialog.open(NewDataEntry, {
      data: {
        id: entry["id"]
      }
    }).afterClosed().subscribe((id) => this.refresh())
  }
}

class DataEntryExplorationDataSource extends DataSource<DataEntryExploration> {
  constructor(private data_entry_service: DataEntriesService) {
    super();
  }
  connect(_collectionViewer: CollectionViewer): Observable<readonly DataEntryExploration[]> {
    return this.data_entry_service.findAll()
  }

  disconnect(_collectionViewer: CollectionViewer): void { }
}