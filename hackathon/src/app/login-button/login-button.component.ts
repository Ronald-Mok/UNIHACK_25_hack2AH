import { Component, OnInit } from '@angular/core';
import { AuthService } from '../auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login-button',
  templateUrl: './login-button.component.html',
  styleUrls: ['./login-button.component.css'],
  imports: [CommonModule], 
})
export class LoginButtonComponent implements OnInit {
  isLoggedIn = false; 
  constructor(private authService: AuthService) {}

  ngOnInit(): void {

    const storedLogin = localStorage.getItem('isLoggedIn');
    this.isLoggedIn = storedLogin === 'true'; 
  }

  handleAuth() {
    if (this.isLoggedIn) {
     
      this.authService.logout();
      this.isLoggedIn = false;
      localStorage.setItem('isLoggedIn', JSON.stringify(false));
    } else {
    
      this.authService.loginWithGoogle();
      this.isLoggedIn = true;
      localStorage.setItem('isLoggedIn', JSON.stringify(true));
    }
  }
}