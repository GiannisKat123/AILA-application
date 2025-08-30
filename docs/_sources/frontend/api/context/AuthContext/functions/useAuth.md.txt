[**vite-project v0.0.0**](../../../README.md)

***

# Function: useAuth()

> **useAuth**(): [`AuthContextType`](../interfaces/AuthContextType.md)

Defined in: [src/context/AuthContext.tsx:454](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L454)

Hook to access [AuthContextType](../interfaces/AuthContextType.md).

## Returns

[`AuthContextType`](../interfaces/AuthContextType.md)

The current authentication context.

## Remarks

Must be used within an [AuthProvider](AuthProvider.md). Throws an error otherwise.

## Example

```tsx
const { user, loginUser, logoutUser } = useAuth();
```
