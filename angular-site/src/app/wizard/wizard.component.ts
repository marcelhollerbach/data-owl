import { Component } from '@angular/core';
import { MatChipInputEvent, MatChipEditedEvent } from '@angular/material/chips';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { SearchItem, SearchLine, SearchRequst, SearchResult, SearchService } from '../search.service';
import { AbstractControl, AsyncValidatorFn, FormControl, FormGroupDirective, NgForm, ValidationErrors } from '@angular/forms';
import { Observable, map } from 'rxjs';
import { DataSource, CollectionViewer } from '@angular/cdk/collections';
import { EmptyDataSource } from '../utils/EmptyDataSource';
import { SearchBarComponent } from '../utils/search-bar/search-bar.component';


@Component({
  selector: 'app-wizard',
  templateUrl: './wizard.component.html',
  styleUrls: ['./wizard.component.scss']
})
export class WizardComponent {
  dataSource: DataSource<SearchResult> = new EmptyDataSource<SearchResult>;

  constructor(private service: SearchService) {

  }

  search(searchBar: SearchBarComponent) {
    this.dataSource = new DataSearchResult(searchBar.toSearchRequest(), this.service)
  }
}

class DataSearchResult extends DataSource<SearchResult> {
  constructor(private sr : SearchRequst, private service: SearchService) {
    super();
  }

  connect(_collectionViewer: CollectionViewer): Observable<readonly SearchResult[]> {
    return this.service.search(this.sr)
  }

  disconnect(_collectionViewer: CollectionViewer): void { }
}

