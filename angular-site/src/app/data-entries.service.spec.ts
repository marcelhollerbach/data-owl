import { TestBed } from '@angular/core/testing';

import { DataEntriesService } from './data-entries.service';

describe('DataEntriesService', () => {
  let service: DataEntriesService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DataEntriesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
