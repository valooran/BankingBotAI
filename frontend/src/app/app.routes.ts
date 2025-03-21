import { Routes } from '@angular/router';
import { ChatWindowComponent } from './chatbot/chat-window/chat-window.component';
import { LoginComponent } from './auth/login/login.component';
import { RegisterComponent } from './auth/register/register.component';
import { AccountSummaryComponent } from './dashboard/account-summary/account-summary.component';
import { SelfTransferComponent } from './transactions/self-transfer/self-transfer.component';
import { TransactionHistoryComponent } from './transactions/transaction-history/transaction-history.component';
import { AuthGuard } from './auth/auth.guard';


const routes: Routes = [
  { path: 'dashboard', component: AccountSummaryComponent, canActivate: [AuthGuard] },
  { path: 'transfer', component: SelfTransferComponent, canActivate: [AuthGuard] },
  { path: 'history', component: TransactionHistoryComponent, canActivate: [AuthGuard] },
  { path: 'chat', component: ChatWindowComponent, canActivate: [AuthGuard] },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
];