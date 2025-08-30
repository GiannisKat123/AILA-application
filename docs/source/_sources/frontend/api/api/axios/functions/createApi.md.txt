[**vite-project v0.0.0**](../../../README.md)

***

# Function: createApi()

> **createApi**(): [`AxiosInstance`](../interfaces/AxiosInstance.md)

Defined in: [src/api/axios.tsx:41](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/api/axios.tsx#L41)

Axios instance pre-configured for backend API calls.

## Returns

[`AxiosInstance`](../interfaces/AxiosInstance.md)

A preconfigured [AxiosInstance](../interfaces/AxiosInstance.md).

## Remarks

Default configuration:
 - `baseURL`: `/` (assumes proxy in dev or reverse proxy in prod)
 - `withCredentials`: `true` (sends cookies such as JWT)

Switch targets by uncommenting the desired `baseURL`.
