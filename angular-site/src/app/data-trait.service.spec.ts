import { TestBed } from '@angular/core/testing';

import { DataTraitService } from './data-trait.service';

describe('DataClassesService', () => {
  let service: DataTraitService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DataTraitService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
