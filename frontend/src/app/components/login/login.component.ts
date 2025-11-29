import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.css']
})
export class LoginComponent {
    email = '';
    password = '';
    error = '';

    constructor(private api: ApiService, private router: Router) { }

    login() {
        this.api.login({ username: this.email, password: this.password }).subscribe({
            next: (res) => {
                this.api.setToken(res.access_token);
                this.router.navigate(['/chat']);
            },
            error: (err) => {
                this.error = 'Invalid credentials';
                console.error(err);
            }
        });
    }
}
