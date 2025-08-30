[**vite-project v0.0.0**](../../README.md)

***

# context/AuthContext

Provides global authentication and user data management across the React app.

Core Responsibilities:
----------------------
1. Authentication lifecycle:
   - login, logout, register
   - verify user sessions with backend
   - resend verification codes

2. User state management:
   - Tracks current logged-in user (`user`)
   - Maintains user's conversations (`conversations`)
   - Maintains messages in active conversation (`userMessages`)

3. Conversation + Message features:
   - Create and rename conversations
   - Fetch user conversations
   - Create new messages
   - Fetch user messages
   - Submit feedback on messages

4. Context Hook:
   - `useAuth()` to access user state and actions

Integration:
------------
Wrap your app in the `AuthProvider` so child components can
consume authentication context via `useAuth()`.

## Remarks

Provides global authentication and user data management across the React app.

## Example

```tsx
  <AuthProvider>
    <App />
  </AuthProvider>

  const { user, loginUser, logoutUser } = useAuth();
```

## Interfaces

- [AuthContextType](interfaces/AuthContextType.md)

## Variables

- [AuthContext](variables/AuthContext.md)

## Functions

- [AuthProvider](functions/AuthProvider.md)
- [useAuth](functions/useAuth.md)
