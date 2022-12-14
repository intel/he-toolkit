import { Injectable } from "@angular/core";
import * as moment from "moment";
import { HttpClient, HttpErrorResponse, HttpHeaders } from "@angular/common/http";
import { catchError, Observable, shareReplay, tap, throwError } from "rxjs";
import jwt_decode from 'jwt-decode';
import { environment } from "src/environments/environment";

@Injectable({
    providedIn: "root"
})
export class AuthService {
    // #region Properties (3)

    private loginUrl = `${environment.urls.auth}/login`;
    private registerUrl = `${environment.urls.auth}/register`;

    public httpOptions = {
        headers: new HttpHeaders({
            "Content-Type": "application/json"
        }),
        // withCredentials: true
    };
    public userName: string = "";

    // #endregion Properties (3)

    // #region Constructors (1)

    constructor(private httpClient: HttpClient) { }

    // #endregion Constructors (1)

    // #region Public Methods (7)

    public getDecodedAccessToken(): any {
        try {
            const accessToken = localStorage.getItem("access_token");
            if (!accessToken) {
                return null;
            }

            return jwt_decode(accessToken);

        } catch (Error) {
            return null;
        }
    }

    public getExpiration() {
        const expiration = localStorage.getItem("expires_at");
        if (!expiration) {
            return moment();
        }

        const expiresAt = JSON.parse(expiration);
        return moment(expiresAt);
    }

    public isLoggedIn(): boolean {
        if (this.getExpiration) {
            return moment().isBefore(this.getExpiration());
        }

        return false;
    }

    public isLoggedOut(): boolean {
        return !this.isLoggedIn();
    }

    public login(email: string, password: string): Observable<any> {
        const body = {
            "email": email,
            "password": password
        }
        return this.httpClient.post<any>(this.loginUrl, body)
            .pipe(
                tap(res => this.setSession(res)),
                shareReplay(),
                catchError((error: HttpErrorResponse) => {
                    return throwError(() => new Error(`Error login in. ${error.statusText || "Unknown"} `));
                })
            );
    }

    public logout(): void {
        localStorage.removeItem("access_token");
        localStorage.removeItem("expires_at");
    }

    public register(username: string, email: string, password: string): Observable<any> {
        const body = {
            "username": username,
            "email": email,
            "password": password
        }
        return this.httpClient.post<any>(this.registerUrl, body)
            .pipe(
                catchError((error: HttpErrorResponse) => {
                    return throwError(() => new Error(`Error register in. ${error.statusText || "Unknown"} `));
                })
            );
    }

    // #endregion Public Methods (7)

    // #region Private Methods (1)

    private setSession(authResult: any) {
        const expiresAt = moment().add(authResult.expires_at, "seconds");
        localStorage.setItem("access_token", authResult.access_token);
        localStorage.setItem("expires_at", JSON.stringify(expiresAt.valueOf()));
    }

    // #endregion Private Methods (1)
}
