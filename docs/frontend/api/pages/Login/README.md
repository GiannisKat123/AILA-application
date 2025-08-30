[**vite-project v0.0.0**](../../README.md)

***

# pages/Login

## Remarks

Renders the login page. Authenticates via [useAuth](../../context/AuthContext/functions/useAuth.md).

Features:
- Username & password input fields
- Calls the AuthContext `loginUser` to authenticate
- Handles both success and error flows:
  - If user is verified → navigate to /chat
  - If user is NOT verified → resend code & redirect to /register
  - If authentication fails → display error message
- Resets username/password fields on error
- Uses TailwindCSS for styling 

Behavior:
- Success + verified → redirect `/chat`
- Success + unverified → resend code & redirect `/register`
- Failure → show error

Uses TailwindCSS for styling.

Dependencies:
- useAuth (AuthContext)
- react-router-dom (navigation)

## Example

```tsx
import Login from './pages/Login';
<Route path="/login" element={<Login />} />
```

## Functions

- [Login](functions/Login.md)

## References

### default

Renames and re-exports [Login](functions/Login.md)
