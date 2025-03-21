import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';

@Component({
  selector: 'app-self-transfer',
  imports: [],
  templateUrl: './self-transfer.component.html',
  styleUrl: './self-transfer.component.css'
})
export class SelfTransferComponent {
  fromAccount = '';
  toAccount = '';
  amount = 0;
  
  constructor(private http: HttpClient) {}
  
  transfer() {
    const token = localStorage.getItem('token');
    const payload = { from: this.fromAccount, to: this.toAccount, amount: this.amount };
  
    this.http.post('http://localhost:8000/api/transfer/self', payload, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe((res: any) => {
      alert('Transfer Successful!');
    });
  }
}
