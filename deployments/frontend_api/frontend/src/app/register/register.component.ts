import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
    selector: 'app-register',
    templateUrl: './register.component.html',
    styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {
    // #region Properties (1)

    public registerForm = this.formBuilder.group({
        username: '',
        email: '',
        password: ''
    });

    // #endregion Properties (1)

    // #region Constructors (1)

    constructor(private authService: AuthService,
        private formBuilder: FormBuilder,
        private router: Router) { }

    // #endregion Constructors (1)

    // #region Public Methods (2)

    public ngOnInit(): void {
    }

    public onSubmit(): void {
        const username = this.registerForm.get('username')?.value;
        const email = this.registerForm.get('email')?.value;
        const password = this.registerForm.get('password')?.value;
        if (this.registerForm.get('username') !== null &&
            this.registerForm.get('email') !== null &&
            this.registerForm.get('password') !== null) {
            this.authService.register(username, email, password).subscribe(
                {
                    next: () => {
                        this.router.navigateByUrl('/');
                    }
                }
            );
        }
    }

    // #endregion Public Methods (2)
}
