import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timer, Subscription } from 'rxjs';
import { tap, switchMap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private accessToken: string;
  private refreshToken: string;
  private tokenExpiryTime: number;
  private refreshSubscription: Subscription;

  constructor(private http: HttpClient) {}

  getAccessToken(): string {
    return this.accessToken;
  }

  setTokens(accessToken: string, refreshToken: string, expiresIn: number) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    this.tokenExpiryTime = Date.now() + expiresIn * 1000;

    // Schedule token refresh
    this.scheduleTokenRefresh();
  }

  refreshToken(): Observable<any> {
    return this.http.post<any>('/api/refresh-token', { refreshToken: this.refreshToken }).pipe(
      tap(tokens => {
        this.setTokens(tokens.accessToken, tokens.refreshToken, tokens.expiresIn);
      })
    );
  }

  logout() {
    this.accessToken = null;
    this.refreshToken = null;
    if (this.refreshSubscription) {
      this.refreshSubscription.unsubscribe();
    }
    // Implement further logout logic (e.g., redirect to login)
  }

  private scheduleTokenRefresh() {
    if (this.refreshSubscription) {
      this.refreshSubscription.unsubscribe();
    }

    const expiresIn = this.tokenExpiryTime - Date.now();
    const refreshTime = expiresIn - (5 * 60 * 1000); // Refresh 5 minutes before expiry

    if (refreshTime > 0) {
      this.refreshSubscription = timer(refreshTime).pipe(
        switchMap(() => this.refreshToken())
      ).subscribe();
    }
  }
}