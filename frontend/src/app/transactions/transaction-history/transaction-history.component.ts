import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AccountService } from '../../account/account.service';

@Component({
  selector: 'app-transaction-history',
  imports: [CommonModule, FormsModule],
  templateUrl: './transaction-history.component.html',
  styleUrl: './transaction-history.component.css'
})
export class TransactionHistoryComponent {
  transactions: any[] = [];
  filters = {
    from_date: '',
    to_date: '',
    account_number: '',
    page: 1,
    limit: 10
  };
  total = 0;

  constructor(private accountService: AccountService) {}
  
  ngOnInit(): void {
    this.loadTransactions();
    // this.accountService.getTransactions().subscribe({
    //   next: (res: any) => {
    //     this.transactions = res;
    //   },
    //   error: () => {
    //     alert('Failed to load transactions');
    //   }
    // });
  }
    
  loadTransactions(): void {
    const filtered: any = {};
  
    if (this.filters.from_date) filtered.from_date = this.filters.from_date;
    if (this.filters.to_date) filtered.to_date = this.filters.to_date;
    if (this.filters.account_number) filtered.account_number = this.filters.account_number;
  
    filtered.page = this.filters.page;
    filtered.limit = this.filters.limit;
  
    this.accountService.getTransactions(filtered).subscribe({
      next: (res: any) => {
        this.transactions = res.transactions;
        this.total = res.total;
      },
      error: () => alert('Failed to load transactions')
    });
  }
  
  
  onPageChange(next: boolean): void {
    this.filters.page += next ? 1 : -1;
    this.loadTransactions();
  }
  
}
