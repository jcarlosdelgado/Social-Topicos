import { Routes } from '@angular/router';
import { ContentGeneratorComponent } from './components/content-generator/content-generator.component';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
<<<<<<< HEAD
=======
import { QueueDashboardComponent } from './components/queue-dashboard/queue-dashboard.component';
import { AdminQueueComponent } from './components/admin-queue/admin-queue';
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a

export const routes: Routes = [
    { path: '', redirectTo: '/chat', pathMatch: 'full' },
    { path: 'login', component: LoginComponent },
    { path: 'register', component: RegisterComponent },
<<<<<<< HEAD
    { path: 'chat', component: ContentGeneratorComponent }
=======
    { path: 'chat', component: ContentGeneratorComponent }, // We'll update this component to handle history
    { path: 'queue', component: QueueDashboardComponent },
    { path: 'admin/queue', component: AdminQueueComponent }
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a
];
