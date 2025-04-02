import { Component } from '@angular/core';
import { ChatbotService } from '../chatbot.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-chat-window',
  imports: [FormsModule, CommonModule],
  templateUrl: './chat-window.component.html',
  styleUrls: ['./chat-window.component.css']
})
export class ChatWindowComponent {
  messages: { sender: string; text: string }[] = [];
  userInput: string = '';
  isOpen: boolean = false;

  constructor(private chatbotService: ChatbotService) {}

  toggleChat(): void {
    this.isOpen = !this.isOpen;
  }

  sendMessage(): void {
    const message = this.userInput.trim();
    if (!message) return;

    this.messages.push({ sender: 'You', text: message });

    this.chatbotService.sendMessage(message).subscribe({
      next: (res) => {
        this.messages.push({ sender: 'Bot', text: res.reply });
      },
      error: (err) => {
        const msg = err.error?.detail || 'An error occurred';
        this.messages.push({ sender: 'Bot', text: `⚠️ ${msg}` });
      }
    });

    this.userInput = '';
  }
}
