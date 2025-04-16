import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Router } from '@angular/router';
import { AuthService } from './auth/auth.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ChatWindowComponent } from './chatbot/chat-window/chat-window.component';
import { ViewChild } from '@angular/core';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet,FormsModule, CommonModule,RouterModule, ChatWindowComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'frontend';
  constructor(public auth: AuthService, private router: Router) {}
  @ViewChild(ChatWindowComponent) chatWindow!: ChatWindowComponent;
  logout() {
    this.auth.logout();
    this.chatWindow.clearMessages();
    this.router.navigate(['/login']);
  }

  showNav(): boolean {
    const route = this.router.url;
    return !['/login', '/register'].includes(route);
  }
}
