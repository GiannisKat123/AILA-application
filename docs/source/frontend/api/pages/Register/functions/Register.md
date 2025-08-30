[**vite-project v0.0.0**](../../../README.md)

***

# Function: Register()

> **Register**(): `undefined` \| `Element`

Defined in: [src/pages/Register.tsx:77](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/pages/Register.tsx#L77)

Register component — renders the registration & verification flow.

## Returns

`undefined` \| `Element`

## Remarks

Provides a two-step flow:
1. **Registration** — collects username, email, and password, validates inputs,
   and calls AuthContextType.registerUser \| registerUser.
2. **Verification** — prompts for a one-time code sent by email, calls
   AuthContextType.verifyCodeUser \| verifyCodeUser, and allows resending via
   AuthContextType.resendCode \| resendCode.

## Responsibilities
- Collect user credentials (username, email, password + confirm).
- Validate password match and enforce backend policy.
- Submit registration request to backend via `registerUser`.
- Transition to verification phase if registration succeeds.
- Display countdown timer and manage resend code functionality.
- On successful verification → navigate to `/chat`.

## Props
None. Uses global state/actions via [useAuth](../../../context/AuthContext/functions/useAuth.md).

## Returns
A React element that conditionally renders either:
- Registration form (step 1), or
- Email verification form (step 2).

## Example
```tsx
import { Register } from "./pages/Register";

<Route path="/register" element={<Register />} />
```
