[**vite-project v0.0.0**](../../../README.md)

***

# Function: registerAPI()

> **registerAPI**(`username`, `password`, `email`): `Promise`\<`boolean` \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

Defined in: [src/services/AuthService.tsx:119](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/services/AuthService.tsx#L119)

Register a new user.

## Parameters

### username

`string`

Desired username

### password

`string`

Desired password (policy enforced server-side)

### email

`string`

User email (verification code sent here)

## Returns

`Promise`\<`boolean` \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

- On success: `true`
 - On failure: `{ error_message: string }`
