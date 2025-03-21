import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';

@Component({
  selector: 'app-account-summary',
  imports: [],
  templateUrl: './account-summary.component.html',
  styleUrl: './account-summary.component.css'
})
export class AccountSummaryComponent {
  account: any;

  constructor(private http: HttpClient) {}
  
  ngOnInit() {
    const token = localStorage.getItem('token');
    this.http.get('http://localhost:8000/api/account', {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe(data => this.account = data);
  }
}
