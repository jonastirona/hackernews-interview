/**
 * Application configuration module.
 * 
 * This module configures:
 * - HTTP client with interceptors
 * - Application providers
 * - Environment-specific settings
 */
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    // Configure router with application routes
    provideRouter(routes),
    
    // Configure HTTP client
    provideHttpClient()
  ]
}; 