import { Component } from '@angular/core';
import { LoginButtonComponent } from './login-button/login-button.component';
import { CommonModule } from '@angular/common';
import { DashboardComponent } from './dashboard/dashboard.component';

@Component({
  selector: 'app-root',
  standalone: true,
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  imports: [LoginButtonComponent, CommonModule, DashboardComponent],
})
export class AppComponent {
  title = 'hackathon';

  get isLoggedIn(): boolean {
    return localStorage.getItem('isLoggedIn') === 'true';
  }
}
