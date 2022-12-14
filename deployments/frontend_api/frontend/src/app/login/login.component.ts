import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
    // #region Properties (1)

    public loginForm = this.formBuilder.group({
        email: '',
        password: ''
    });

    // #endregion Properties (1)

    // #region Constructors (1)

    constructor(
        private authService: AuthService,
        private formBuilder: FormBuilder,
        private router: Router
    ) { }

    // #endregion Constructors (1)

    // #region Public Methods (2)

    public ngOnInit(): void {
        if (this.authService.isLoggedIn()) {
            this.router.navigate(['/dashboard']);
        }
    }

    public onSubmit(): void {
        const email = this.loginForm.get('email')?.value;
        const password = this.loginForm.get('password')?.value;
        if (this.loginForm.get('email') !== null && this.loginForm.get('password') !== null) {
            this.authService.login(email, password).subscribe(
                {
                    next: (token: any) => {
                        console.log(token);
                        this.router.navigateByUrl('/');
                    }
                }
            );
        }
    }

    // #endregion Public Methods (2)
}
