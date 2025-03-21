import { Component } from '@angular/core';
import { ChatbotService } from '../chatbot.service';

@Component({
  selector: 'app-chat-window',
  templateUrl: './chat-window.component.html',
})
export class ChatWindowComponent {
  messages: { sender: string, text: string }[] = [];
  userInput = '';
  
  constructor(private chatbotService: ChatbotService) {}

  sendMessage() {
    if (!this.userInput.trim()) return;

    const userMsg = this.userInput;
    this.messages.push({ sender: 'user', text: userMsg });
    this.userInput = '';

    this.chatbotService.sendMessage(userMsg).subscribe((res: any) => {
      this.messages.push({ sender: 'bot', text: res.reply });
    });
  }
}
