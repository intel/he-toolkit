import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, map, Observable, throwError } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
    providedIn: 'root'
})
export class JobService {
    // #region Properties (2)

    private jobsUrl = `${environment.urls.apiJobs}`;

    public httpOptions = {
        headers: new HttpHeaders({
            "Content-Type": "application/json"
        }),
        withCredentials: true
    };

    // #endregion Properties (2)

    // #region Constructors (1)

    constructor(private httpClient: HttpClient) { }

    // #endregion Constructors (1)

    // #region Public Methods (3)

    public createJob(file: any): Observable<any> {
        const httpOptions = {
            headers: new HttpHeaders({
                "Content-Type": "application/json"
            }),
            withCredentials: true
        };
        return this.httpClient.post<any>(this.jobsUrl, file, this.httpOptions)
            .pipe(
                catchError((error: HttpErrorResponse) => {
                    return throwError(() => new Error(`Error in jobs. ${error.statusText || "Unknown"} `));
                })
            );
    }

    public decryptJob(jobId: string): Observable<any> {
        return this.httpClient.get<any>(`${this.jobsUrl}/${jobId}/decrypt`, this.httpOptions)
            .pipe(
                catchError((error: HttpErrorResponse) => {
                    return throwError(() => new Error(`Error in decrypt jobs. ${error.statusText || "Unknown"} `));
                })
            );
    }

    public downloadJobResult(jobId: string): Observable<any> {
        const httpOptions = {
            headers: new HttpHeaders({
                "Content-Type": "application/json"
            }),
            withCredentials: true,
            responseType: 'blob' as 'json'
        };
        return this.httpClient.get<any>(`${this.jobsUrl}/${jobId}/result`, httpOptions)
            .pipe(
                catchError((error: HttpErrorResponse) => {
                    return throwError(() => new Error(`Error in download job result. ${error.statusText || "Unknown"} `));
                })
            );
    }

    public getJobs(): Observable<any> {
        return this.httpClient.get<any>(this.jobsUrl, this.httpOptions)
            .pipe(
                catchError((error: HttpErrorResponse) => {
                    return throwError(() => new Error(`Error in jobs. ${error.statusText || "Unknown"} `));
                })
            );
    }

    // #endregion Public Methods (3)
}
