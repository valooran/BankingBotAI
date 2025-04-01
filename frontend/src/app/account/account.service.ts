import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { AuthService } from '../auth/auth.service';

@Injectable({ providedIn: 'root' })
export class AccountService {
  private apiUrl = `${environment.apiUrl}/account`;

  constructor(private http: HttpClient, private auth: AuthService) {}

  private getHeaders() {
    const token = this.auth.getToken();
    console.log("Using token:", token);
    return new HttpHeaders().set('token', token ? token : '');
  }

  createAccount(accountType: string) {
    return this.http.post(`${this.apiUrl}/create`, { account_type: accountType }, {
      headers: this.getHeaders()
    });
  }

  getSummary() {
    return this.http.get(`${this.apiUrl}/summary`, {
      headers: this.getHeaders()
    });
  }

  transferFunds(from: string, to: string, amount: number) {
    return this.http.post(`${this.apiUrl}/transfer`, {
      from_account: from,
      to_account: to,
      amount: amount
    }, {
      headers: this.getHeaders()
    });
  }

  getTransactions() {
    return this.http.get(`${this.apiUrl}/transactions`, {
      headers: this.getHeaders()
    });
  }
}
