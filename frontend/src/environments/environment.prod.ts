/**
 * Production environment configuration.
 * 
 * This file contains environment-specific settings for production:
 * - production flag set to true for production optimizations
 * - API URL using relative path for production deployment
 */
export const environment = {
  /** Flag indicating production environment */
  production: true,
  /** Base URL for API requests in production */
  apiUrl: '/api'
}; 