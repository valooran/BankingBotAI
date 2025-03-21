import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';

@Component({
  selector: 'app-transaction-history',
  imports: [],
  templateUrl: './transaction-history.component.html',
  styleUrl: './transaction-history.component.css'
})
export class TransactionHistoryComponent {
  transactions: any[] = [];

  constructor(private http: HttpClient) {}
  
  ngOnInit() {
    const token = localStorage.getItem('token');
    this.http.get('http://localhost:8000/api/transactions', {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe((data: any) => {
      this.transactions = data;
    });
  }
  
}
