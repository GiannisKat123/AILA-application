[**vite-project v0.0.0**](../../README.md)

***

# api/axios

Axios API Client
----------------
This module configures a reusable Axios instance for making HTTP requests
to the backend API. It ensures consistent base URL and credential handling.

Why centralize Axios config?
- Avoids repeating baseURL and headers in every call.
- Makes it easier to update backend URLs (production vs. development).
- Enables credential sharing (cookies, auth tokens).

## Remarks

Centralized Axios instance for backend API calls. Ensures consistent
`baseURL` handling and credential sharing across requests.

## Example

```ts
import api from './api'
const res = await api.get('/user_conversations')
```

## See

[Factory helper](functions/createApi.md) for testing or per‑request overrides.

## Interfaces

- [AxiosInstance](interfaces/AxiosInstance.md)

## Variables

- [api](variables/api.md)

## Functions

- [createApi](functions/createApi.md)

## References

### default

Renames and re-exports [api](variables/api.md)
