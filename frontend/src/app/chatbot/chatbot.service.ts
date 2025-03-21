import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChatbotService {
  private apiUrl = 'http://localhost:8000/chat'; // FastAPI backend endpoint

  constructor(private http: HttpClient) {}

  sendMessage(message: string): Observable<any> {
    return this.http.post(this.apiUrl, { message });
  }
}
