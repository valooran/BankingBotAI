import { Routes } from '@angular/router';
import { ChatWindowComponent } from './chatbot/chat-window/chat-window.component';

const routes: Routes = [
    { path: 'chat', component: ChatWindowComponent },
    { path: '', redirectTo: 'chat', pathMatch: 'full' },
  ];