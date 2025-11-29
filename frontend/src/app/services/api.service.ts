import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8080/api';

  private tokenKey = 'auth_token';

  constructor(private http: HttpClient) { }

  private getHeaders() {
    const token = localStorage.getItem(this.tokenKey);
    return {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    };
  }

  // Auth
  login(data: any): Observable<any> {
    // OAuth2PasswordRequestForm expects form-urlencoded data
    const formData = new URLSearchParams();
    formData.set('username', data.username);
    formData.set('password', data.password);

    return this.http.post(`${this.apiUrl}/auth/login`, formData.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
  }

  register(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/register`, data);
  }

  setToken(token: string) {
    localStorage.setItem(this.tokenKey, token);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  logout() {
    localStorage.removeItem(this.tokenKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  // Chat
  getChats(): Observable<any> {
    return this.http.get(`${this.apiUrl}/chats/`, this.getHeaders());
  }

  createChat(title: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/chats/`, { title }, this.getHeaders());
  }

  getMessages(chatId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/chats/${chatId}/messages`, this.getHeaders());
  }

  sendMessage(chatId: number, content: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/chats/${chatId}/messages`, { content }, this.getHeaders());
  }

  // Content Generation
  generateContent(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/generate`, data);
  }

  publishContent(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/publish`, data);
  }

  // Publications History
  getPublications(skip: number = 0, limit: number = 100): Observable<any> {
    return this.http.get(`${this.apiUrl}/publications?skip=${skip}&limit=${limit}`);
  }

  getMyPublications(skip: number = 0, limit: number = 100): Observable<any> {
    return this.http.get(`${this.apiUrl}/publications/me?skip=${skip}&limit=${limit}`, this.getHeaders());
  }

  getPublication(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/publications/${id}`);
  }
}
