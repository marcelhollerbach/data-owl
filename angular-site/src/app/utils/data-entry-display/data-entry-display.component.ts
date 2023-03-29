import { DataSource } from '@angular/cdk/collections';
import { Component, Input } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { DataEntryExploration, DataEntriesService } from '../../data-entries.service';
import { EmptyDataSource } from '../EmptyDataSource';
import { NewDataEntry } from './modal/new-data-entry';

@Component({
  selector: 'app-data-entry-display',
  templateUrl: './data-entry-display.component.html',
  styleUrls: ['./data-entry-display.component.scss']
})
export class DataEntryDisplayComponent<T> {

  private _dataSourceProducer!: () => DataSource<T>;
  private _backendChangedCb: () => void = () => {};


  @Input('dataSourceProducer') public set dataSourceProducer(value: DataSource<T>) {
    this.dataSource = value;
  }

  @Input('backendChangedCb') public set backendChangedCb(value: () => void) {
    this._backendChangedCb = value
  }

  dataSource: DataSource<T>;
  
  displayedColumns = ['Name', 'Description'];

  constructor(public create_dialog: MatDialog, public detail_dialog: MatDialog, private data_entry_service: DataEntriesService) {
    this.dataSource = new EmptyDataSource<T>();
  }
  openSingleCreationDialog(): void {
    this.show_entry({ id: "" })
  }
  show_entry(entry: any) {
    this.create_dialog.open(NewDataEntry, {
      data: {
        id: entry["id"]
      }
    }).afterClosed().subscribe((id) => this._backendChangedCb())
  }
}

