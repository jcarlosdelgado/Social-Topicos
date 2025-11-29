import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
    selector: 'app-register',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './register.component.html',
    styleUrls: ['./register.component.css']
})
export class RegisterComponent {
    email = '';
    password = '';
    confirmPassword = '';
    error = '';

    constructor(private api: ApiService, private router: Router) { }

    register() {
        if (this.password !== this.confirmPassword) {
            this.error = 'Passwords do not match';
            return;
        }

        this.api.register({ email: this.email, password: this.password }).subscribe({
            next: (res) => {
                // Auto login or redirect to login
                this.router.navigate(['/login']);
            },
            error: (err) => {
                this.error = 'Registration failed. Email might be taken.';
                console.error(err);
            }
        });
    }
}
