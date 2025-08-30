[**vite-project v0.0.0**](../../README.md)

***

# services/AuthService

Axios-based client for the AILA backend API.

## Remarks

Axios client for the AILA backend. Encapsulates all HTTP calls:
- Login, logout, register, verify
- Conversations (create, fetch, rename)
- Messages (create, fetch)
- Feedback submission
- Request endpoint (chat)

Responsibilities
----------------
- Encapsulates all HTTP calls (login, register, verify, conversations, messages, feedback, logout).
- Normalizes error handling and return shapes for the frontend.

Conventions
-----------
- All requests use `withCredentials: true` to send HttpOnly cookies (JWT).
- On Axios errors, functions return `{ error_message: string }` where applicable.
- Functions that don't need a payload from the server return `boolean | undefined`.
- Functions that must return data bubble it through `.data` as typed.

Conventions:
- All requests → `withCredentials: true` (send cookies)
- Errors → return `{ error_message }` where possible
- Functions without data → return `boolean | undefined`
- Functions with data → bubble `.data`

## Example

```ts
import { loginAPI } from '../services/AuthService';
const res = await loginAPI('alice', 's3cret');
if ('user_details' in res) {
console.log(res.user_details.username);
}
```

## Functions

- [createConversationAPI](functions/createConversationAPI.md)
- [createMessageAPI](functions/createMessageAPI.md)
- [getConversationsAPI](functions/getConversationsAPI.md)
- [getUserMessagesAPI](functions/getUserMessagesAPI.md)
- [loginAPI](functions/loginAPI.md)
- [logoutAPI](functions/logoutAPI.md)
- [registerAPI](functions/registerAPI.md)
- [renameConversationAPI](functions/renameConversationAPI.md)
- [requestAPI](functions/requestAPI.md)
- [resendCodeAPI](functions/resendCodeAPI.md)
- [userFeedbackAPI](functions/userFeedbackAPI.md)
- [verifyAPI](functions/verifyAPI.md)
- [verifyUser](functions/verifyUser.md)
