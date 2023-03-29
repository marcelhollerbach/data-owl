import { DataSource, CollectionViewer } from '@angular/cdk/collections';
import { EMPTY, Observable } from 'rxjs';


export class EmptyDataSource<T> extends DataSource<T> {
  constructor() {
    super();
  }
  connect(_collectionViewer: CollectionViewer): Observable<readonly T[]> {
    return EMPTY;
  }

  disconnect(_collectionViewer: CollectionViewer): void { }
}
