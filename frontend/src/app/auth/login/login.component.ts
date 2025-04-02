import { Component } from '@angular/core';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-login',
  imports: [FormsModule ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  email = '';
  password = '';
  
  constructor(private authService: AuthService, private router: Router) {}
  
  login() {
    this.authService.login(this.email, this.password).subscribe({
      next: (res: any) => {
        this.authService.storeToken(res.token);
        this.router.navigate(['/dashboard']);
      },
      error: () => alert('Login failed')
    });
  }
}


