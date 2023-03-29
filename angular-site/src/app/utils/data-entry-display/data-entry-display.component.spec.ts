import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DataEntryDisplayComponent } from './data-entry-display.component';

describe('DataEntryDisplayComponent', () => {
  let component: DataEntryDisplayComponent;
  let fixture: ComponentFixture<DataEntryDisplayComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DataEntryDisplayComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DataEntryDisplayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
