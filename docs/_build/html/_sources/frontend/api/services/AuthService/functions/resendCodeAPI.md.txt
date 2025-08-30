[**vite-project v0.0.0**](../../../README.md)

***

# Function: resendCodeAPI()

> **resendCodeAPI**(`username`, `email`): `Promise`\<`undefined` \| `boolean`\>

Defined in: [src/services/AuthService.tsx:172](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/services/AuthService.tsx#L172)

Resend the verification code to a user.

## Parameters

### username

`string`

Username

### email

`string`

Registered email address

## Returns

`Promise`\<`undefined` \| `boolean`\>

- On success: `true`
 - On failure: `undefined` (and logs error)
