/**
 * Application routing configuration.
 * 
 * This module defines the application's routing structure.
 * Currently, the application uses a single route for the main view
 * since it's a single-page application focused on displaying
 * Hacker News stories.
 */
import { Routes } from '@angular/router';
import { AppComponent } from './app.component';

export const routes: Routes = [
  // Main route for the application
  // The AppComponent handles all the functionality
  { path: '', component: AppComponent }
];
