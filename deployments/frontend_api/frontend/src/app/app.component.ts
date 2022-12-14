import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './services/auth.service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent {
    // #region Properties (1)

    public title = 'frontend';
    public userName: string = "";

    // #endregion Properties (1)

    // #region Constructors (1)

    constructor(
        public router: Router,
        public authService: AuthService
    ) {
        if (!this.authService.isLoggedIn()) {
            this.router.navigate(['login']);
        }
    }

    // #endregion Constructors (1)

    // #region Public Methods (1)

    public logout() {
        this.authService.logout();
        this.router.navigate(['/login']);
    }

    // #endregion Public Methods (1)
}
