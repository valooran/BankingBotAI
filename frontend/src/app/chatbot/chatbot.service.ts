import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChatbotService {
  private apiUrl = 'http://127.0.0.1:8000/api/chat';

  constructor(private http: HttpClient) {}

  sendMessage(message: string): Observable<{ reply: string }> {
    const token = localStorage.getItem('token') || '';

    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      token: token
    });

    return this.http.post<{ reply: string }>(
      this.apiUrl,
      { message },
      { headers }
    );
  }
}
