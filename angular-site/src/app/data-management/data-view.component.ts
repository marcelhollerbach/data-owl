import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Observable } from 'rxjs';
import { DataEntriesService, DataEntryExploration } from '../data-entries.service';
import { DataSource } from '@angular/cdk/table';
import { CollectionViewer } from '@angular/cdk/collections';
import { EmptyDataSource } from '../utils/EmptyDataSource';


@Component({
  selector: 'app-data-view',
  templateUrl: './data-view.component.html',
  styleUrls: ['./data-view.component.scss']
})
export class DataViewComponent {
  dataSource: DataSource<DataEntryExploration> = new EmptyDataSource<DataEntryExploration>;

  constructor(private data_entry_service: DataEntriesService) {
    this.refresh();
  }
  refresh() {
    this.dataSource = new DataEntryExplorationDataSource(this.data_entry_service);
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
