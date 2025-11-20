import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://127.0.0.1:8080/api';

  constructor(private http: HttpClient) { }

  generateContent(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/generate`, data);
  }

  publishContent(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/publish`, data);
  }
}
