import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TraitManagementComponent } from './trait-management.component';

describe('TraitManagementComponent', () => {
  let component: TraitManagementComponent;
  let fixture: ComponentFixture<TraitManagementComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TraitManagementComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TraitManagementComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
