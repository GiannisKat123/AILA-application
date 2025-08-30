[**vite-project v0.0.0**](../../../README.md)

***

# Function: AuthProvider()

> **AuthProvider**(`children`): `Element`

Defined in: [src/context/AuthContext.tsx:133](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L133)

Provides the authentication context and state to all child components.

## Parameters

### children

React component tree to be wrapped by the provider.

#### children

`ReactNode`

## Returns

`Element`

A React context provider that supplies [AuthContextType](../interfaces/AuthContextType.md) to its children.

## Remarks

- Should wrap your entire application (usually in `main.tsx` or `index.tsx`).
- Exposes authentication and conversation state/actions via [useAuth](useAuth.md).

## Example

```tsx
import { AuthProvider } from "./context/AuthContext";

const root = createRoot(document.getElementById("root")!);
root.render(
  <AuthProvider>
    <App />
  </AuthProvider>
);
```
