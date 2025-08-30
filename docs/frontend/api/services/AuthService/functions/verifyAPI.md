[**vite-project v0.0.0**](../../../README.md)

***

# Function: verifyAPI()

> **verifyAPI**(`username`, `code`): `Promise`\<`boolean` \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

Defined in: [src/services/AuthService.tsx:145](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/services/AuthService.tsx#L145)

Verify a user using a code emailed to them.

## Parameters

### username

`string`

Username to verify

### code

`string`

One-time verification code

## Returns

`Promise`\<`boolean` \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

- On success: `true`
 - On failure: `{ error_message: string }`
