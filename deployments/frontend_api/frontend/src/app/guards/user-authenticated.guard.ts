import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, CanActivateChild, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable, of } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable({
    providedIn: 'root'
})
export class UserAuthenticatedGuard implements CanActivateChild {
    // #region Constructors (1)

    constructor(private authService: AuthService, private router: Router) {
    }

    // #endregion Constructors (1)

    // #region Public Methods (1)

    public canActivateChild(childRoute: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean | UrlTree | Observable<boolean | UrlTree> | Promise<boolean | UrlTree> {
        if (!this.authService.isLoggedIn()) {
            this.router.navigate(['login']);
            return of(false);
        }

        return of(true);
    }

    // #endregion Public Methods (1)
}
