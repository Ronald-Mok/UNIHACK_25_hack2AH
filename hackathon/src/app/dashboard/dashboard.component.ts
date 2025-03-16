import { Component, OnInit } from '@angular/core';
import { AuthService } from '../auth.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
  imports: [CommonModule, FormsModule]
})
export class DashboardComponent implements OnInit {
  user: any = {};  
  analyzedEmails: any[] = []; 

  constructor(public authService: AuthService) {} 

  ngOnInit(): void {
    this.user = this.authService.getUser();

    if (this.user && this.user.email) {
      this.fetchAnalyzedEmails(this.user.email);
    }
  }

  fetchAnalyzedEmails(email: string): void {
    this.authService.fetchAnalyzedEmails(email).subscribe(
      (response: any) => {
        if (response && response.user) {
          this.user = response.user;  
        }
        if (response && response.emails) {
          this.analyzedEmails = response.emails;
          console.log("✅ Analyzed Emails:", this.analyzedEmails);
        } else {
          console.warn("⚠️ No analyzed emails found!");
        }
      },
      (error) => {
        console.error("❌ Error fetching emails:", error);
      }
    );
  }
}
