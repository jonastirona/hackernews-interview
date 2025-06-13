/**
 * Development environment configuration.
 * 
 * This file contains environment-specific settings for development:
 * - production flag set to false for development features
 * - API URL pointing to local development server
 */
export const environment = {
  /** Flag indicating development environment */
  production: false,
  /** Base URL for API requests in development */
  apiUrl: 'http://127.0.0.1:8001'
}; 