import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SelfTransferComponent } from './self-transfer.component';

describe('SelfTransferComponent', () => {
  let component: SelfTransferComponent;
  let fixture: ComponentFixture<SelfTransferComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SelfTransferComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SelfTransferComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
