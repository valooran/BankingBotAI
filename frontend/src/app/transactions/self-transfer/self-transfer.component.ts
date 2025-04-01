import { Component } from '@angular/core';
import { AccountService } from '../../account/account.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; 
import { Router } from '@angular/router';
import { RouterModule } from '@angular/router'; 

@Component({
  standalone: true,
  selector: 'app-self-transfer',
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './self-transfer.component.html',
  styleUrl: './self-transfer.component.css'
})
export class SelfTransferComponent {
  fromAccount = '';
  toAccount = '';
  amount = 0;
  accounts: any[] = [];
  errorMessage: string = '';
  selectedFromBalance: number | null = null;
  selectedToBalance: number | null = null;

  constructor(
    private accountService: AccountService,
    private router: Router
  ) {}
  

  ngOnInit(): void {
    this.loadAccounts();
  }

  loadAccounts(): void {
    this.accountService.getSummary().subscribe({
      next: (res: any) => {
        this.accounts = res;
      },
      error: () => alert('Failed to load accounts')
    });
  }

  onFromChange(): void {
    if (this.fromAccount === this.toAccount) {
      this.toAccount = '';
    }
  
    const selectedAcc = this.accounts.find(acc => acc.account_number === this.fromAccount);
    this.selectedFromBalance = selectedAcc?.balance || null;
  }

  onToChange(): void {
    const selectedAcc = this.accounts.find(acc => acc.account_number === this.toAccount);
    this.selectedToBalance = selectedAcc?.balance || null;
  }

  isFormValid(): boolean {
    return (
      !!this.fromAccount &&
      !!this.toAccount &&
      this.amount > 0 &&
      this.fromAccount !== this.toAccount
    );
  }

  transfer(): void {
    this.errorMessage = '';
  
    if (!this.fromAccount || !this.toAccount || !this.amount) {
      this.errorMessage = 'Please fill all fields.';
      return;
    }
  
    if (this.fromAccount === this.toAccount) {
      this.errorMessage = 'Please select a different account for transfer.';
      return;
    }
  
    if (this.amount <= 0) {
      this.errorMessage = 'Amount must be greater than 0.';
      return;
    }
  
    this.accountService.transferFunds(this.fromAccount, this.toAccount, this.amount).subscribe({
      next: () => {
        alert('Transfer successful! ✅');
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.errorMessage = err.error.detail || 'Transfer failed.';
      }
    });
  }
  
}
