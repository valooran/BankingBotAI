import { Component } from '@angular/core';
import { AccountService } from '../../account/account.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-account-summary',
  imports: [FormsModule, CommonModule],
  templateUrl: './account-summary.component.html',
  styleUrl: './account-summary.component.css'
})
export class AccountSummaryComponent {
  accounts: any[] = [];
  showModal = false;

  newAccountType: string = '';
  initialDeposit: number = 0;

  errorMessage: string = '';
  successMessage: string = '';

  constructor(private accountService: AccountService) {}

  ngOnInit() {
    this.loadAccounts()
  }

  loadAccounts(){
    this.accountService.getSummary().subscribe({
      next: (res: any) => this.accounts = res,
      error: () => alert('Failed to load account summary')
    });
  }

  createAccount(): void {
    if (!this.newAccountType || this.initialDeposit < 0) {
      this.errorMessage = 'Please fill in valid account details.';
      return;
    }

    this.accountService.createAccount(this.newAccountType, this.initialDeposit).subscribe({
      next: () => {
        this.successMessage = 'Account created successfully!';
        this.errorMessage = '';
        this.showModal = false;
        this.resetForm();
        this.loadAccounts(); // Refresh list
      },
      error: (err) => {
        console.error('Account creation failed:', err);
        this.errorMessage = err.error?.detail || 'Failed to create account.';
        this.successMessage = '';
      }
    });
  }

  // Reset modal form fields
  resetForm(): void {
    this.newAccountType = '';
    this.initialDeposit = 0;
  }
}
