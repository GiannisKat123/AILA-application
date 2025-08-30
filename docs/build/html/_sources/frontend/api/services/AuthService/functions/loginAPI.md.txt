[**vite-project v0.0.0**](../../../README.md)

***

# Function: loginAPI()

> **loginAPI**(`username`, `password`): `Promise`\<[`LoginAPIOutput`](../../../models/Types/type-aliases/LoginAPIOutput.md) \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

Defined in: [src/services/AuthService.tsx:66](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/services/AuthService.tsx#L66)

Login with username/password.

## Parameters

### username

`string`

Account username

### password

`string`

Account password (plaintext)

## Returns

`Promise`\<[`LoginAPIOutput`](../../../models/Types/type-aliases/LoginAPIOutput.md) \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

- On success: `{ user_details: UserProfile }`
 - On failure: `{ error_message: string }`
