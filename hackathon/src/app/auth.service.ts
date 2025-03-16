import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private API_URL = 'http://127.0.0.1:8000/api';
  private GOOGLE_AUTH_URL = `${this.API_URL}/auth/google/`; 
  private LOGIN_URL = `${this.API_URL}/login/`; 
  private EMAILS_URL = `${this.API_URL}/get_analyzed_emails`; 

  private authStatus = new BehaviorSubject<boolean>(this.isUserLoggedIn());
  authStatus$ = this.authStatus.asObservable();

  constructor(private http: HttpClient) {}

  private isUserLoggedIn(): boolean {
    return localStorage.getItem('isLoggedIn') === 'true';
  }

  loginWithGoogle(): void {
    window.location.href = this.GOOGLE_AUTH_URL;
  }

  setUser(userData: any): void {
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('isLoggedIn', 'true');
    this.authStatus.next(true);
  }

  getUser(): any {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  fetchAnalyzedEmails(userEmail: string): Observable<any> {
    return this.http.get(`${this.EMAILS_URL}?email=${encodeURIComponent(userEmail)}`);
  }

  logout(): void {
    localStorage.removeItem('user');
    localStorage.removeItem('isLoggedIn');
    this.authStatus.next(false);
    window.location.href = '/';
  }
}
