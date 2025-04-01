import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { TransactionsRoutingModule } from './transactions-routing.module';
import { SelfTransferComponent } from './self-transfer/self-transfer.component';


@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    FormsModule,
    TransactionsRoutingModule,
    SelfTransferComponent
  ]
})
export class TransactionsModule { }
