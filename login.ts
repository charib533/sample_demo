// Example of storing tokens after login
login(username: string, password: string): Observable<any> {
  return this.http.post<any>('/api/login', { username, password }).pipe(
    tap(tokens => {
      this.setTokens(tokens.accessToken, tokens.refreshToken, tokens.expiresIn);
    })
  );
}