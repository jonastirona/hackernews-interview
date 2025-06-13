/**
 * Main entry point for the Angular application.
 * 
 * This file bootstraps the application by:
 * 1. Importing the root component (AppComponent)
 * 2. Loading application configuration
 * 3. Initializing the application with the provided configuration
 */
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

// Bootstrap the application with the root component and configuration
bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error('Failed to bootstrap application:', err));
