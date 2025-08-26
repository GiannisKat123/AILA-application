/**
 * Axios API Client
 * ----------------
 * This module configures a reusable Axios instance for making HTTP requests
 * to the backend API. It ensures consistent base URL and credential handling.
 *
 * Usage:
 *   import api from './api';
 *
 *   // Example request
 *   const response = await api.get('/user_conversations');
 *
 * Why centralize Axios config?
 * - Avoids repeating baseURL and headers in every call.
 * - Makes it easier to update backend URLs (production vs. development).
 * - Enables credential sharing (cookies, auth tokens).
 */

import axios from 'axios';

/**
 * Axios instance preconfigured for backend API calls.
 *
 * Configuration:
 * - baseURL: "/" → proxied by frontend dev server or Nginx in production.
 *   (Can be swapped to "http://localhost:8080" for local development or
 *   "https://ailademo.fly.dev" in deployment.)
 *
 * - withCredentials: true → ensures cookies (e.g., JWT token) are sent
 *   with each request.
 */
const api = axios.create({
  // baseURL: "https://ailademo.fly.dev", // ✅ Production deployment
  // baseURL: "http://localhost:8080",    // ✅ Local development
  baseURL: "/",                            // ✅ Default: relative path (frontend proxy)
  withCredentials: true,                   // Include cookies for auth
});

export default api;
