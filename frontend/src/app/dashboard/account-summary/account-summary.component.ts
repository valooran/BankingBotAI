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

  constructor(private accountService: AccountService) {}

  ngOnInit() {
    this.accountService.getSummary().subscribe({
      next: (res: any) => this.accounts = res,
      error: () => alert('Failed to load account summary')
    });
  }
}
