[**vite-project v0.0.0**](../../../README.md)

***

# Function: verifyUser()

> **verifyUser**(): `Promise`\<`undefined` \| [`UserProfile`](../../../models/Types/type-aliases/UserProfile.md)\>

Defined in: [src/services/AuthService.tsx:307](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/services/AuthService.tsx#L307)

Verify current session and return user profile from cookie.

## Returns

`Promise`\<`undefined` \| [`UserProfile`](../../../models/Types/type-aliases/UserProfile.md)\>

- On success: `UserProfile`
 - On failure: throws Axios error (caller should handle)
