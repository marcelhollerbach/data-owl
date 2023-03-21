import { TestBed } from '@angular/core/testing';

import { DataTraitManagementService } from './data-trait-management.service';

describe('DataTraitManagementService', () => {
  let service: DataTraitManagementService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DataTraitManagementService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
