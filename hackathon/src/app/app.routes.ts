import { RouterModule, Routes } from '@angular/router';
import { LoginButtonComponent } from './login-button/login-button.component';
import { NgModule } from '@angular/core';
import { DashboardComponent } from './dashboard/dashboard.component';

export const routes: Routes = [
    { path: 'login', component: LoginButtonComponent },
    { path: 'dashboard', component: DashboardComponent } 
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})


export class AppRoutingModule { }