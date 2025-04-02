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

  constructor(private accountService: AccountService) {}
  
  ngOnInit(): void {
    this.accountService.getTransactions().subscribe({
      next: (res: any) => {
        this.transactions = res;
      },
      error: () => {
        alert('Failed to load transactions');
      }
    });
  }
  
}
