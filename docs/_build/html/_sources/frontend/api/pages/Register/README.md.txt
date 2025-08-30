[**vite-project v0.0.0**](../../README.md)

***

# pages/Register

## Remarks

React component that handles **user registration** and **email verification**.

Features:
- New user registration with:
  - username
  - email
  - password (double-entry check)
- Server-side password policy enforced
- Email verification workflow:
  - After successful registration, user must verify via 6-digit code sent to email
  - Code expires in 120s (timer with resend functionality)
  - Resend code button reactivates only after expiration
- Graceful error handling and accessibility with `aria-live`
- TailwindCSS styled form with clear instructions

States:
- `verified`:
   undefined → user not yet registered
   false → registered but awaiting email verification
   true → registration + verification completed → redirected to `/chat`

Dependencies:
- useAuth (AuthContext → RegisterUser, verifyCodeUser, resendCode)
- react-router-dom (navigation)

## Example

```tsx
import Register from './pages/Register';
<Route path="/register" element={<Register />} />
```

## Functions

- [Register](functions/Register.md)

## References

### default

Renames and re-exports [Register](functions/Register.md)
