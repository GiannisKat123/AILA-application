[**vite-project v0.0.0**](../../../README.md)

***

# Function: Login()

> **Login**(): `Element`

Defined in: [src/pages/Login.tsx:70](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/pages/Login.tsx#L70)

Login component — renders the sign-in page.

## Returns

`Element`

## Remarks

Provides username/password login with three outcome flows:
1. **Success & verified** → navigates to `/chat`.
2. **Success but unverified** → resends verification code, then redirects to `/register`.
3. **Failure** → shows an error message and resets input fields.

## Responsibilities
- Collect username & password from the user.
- Call AuthContextType.loginUser \| loginUser via [useAuth](../../../context/AuthContext/functions/useAuth.md).
- Call AuthContextType.resendCode \| resendCode if the user is unverified.
- Manage local state for inputs, loading, and errors.
- Redirect the user appropriately based on login outcome.

## Props
None. This component consumes global state/actions from [useAuth](../../../context/AuthContext/functions/useAuth.md).

## Returns
A styled login form wrapped in TailwindCSS classes.

## Example

```tsx
import { Login } from "./pages/Login";

<Route path="/login" element={<Login />} />
```
