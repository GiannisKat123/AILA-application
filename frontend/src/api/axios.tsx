/**
* @packageDocumentation
*
* Axios API Client
* ----------------
* This module configures a reusable Axios instance for making HTTP requests
* to the backend API. It ensures consistent base URL and credential handling.
*
* Why centralize Axios config?
* - Avoids repeating baseURL and headers in every call.
* - Makes it easier to update backend URLs (production vs. development).
* - Enables credential sharing (cookies, auth tokens).
* 
* @remarks
* Centralized Axios instance for backend API calls. Ensures consistent
* `baseURL` handling and credential sharing across requests.
*
* @example
* ```ts
* import api from './api'
* const res = await api.get('/user_conversations')
* ```
*
* @see {@link createApi | Factory helper} for testing or per‑request overrides.
*/
import axios, { type AxiosInstance } from 'axios';


/**
* Axios instance pre-configured for backend API calls.
* 
* @remarks
* Default configuration:
*  - `baseURL`: `/` (assumes proxy in dev or reverse proxy in prod)
*  - `withCredentials`: `true` (sends cookies such as JWT)
*
* Switch targets by uncommenting the desired `baseURL`.
*
* @returns A preconfigured {@link AxiosInstance}.
 */
function createApi(): AxiosInstance {
  return axios.create({
    // baseURL: 'https://ailademo.fly.dev', // ✅ Production deployment
    baseURL: 'http://localhost:8080', // ✅ Local development
    // baseURL: '/', // ✅ Default: relative path (frontend proxy)
    withCredentials: true, // Include cookies for auth
  })
}

/**
 * Exported Axios client for general use.
 *
 * @see createApi
 * @example
 * ```ts
 * import { api } from './api'
 * const res = await api.get('/user_conversations')
 * ```
 */
export const api: AxiosInstance = createApi();
export default api;
export { createApi };
export type { AxiosInstance };

