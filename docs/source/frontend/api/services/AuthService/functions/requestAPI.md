[**vite-project v0.0.0**](../../../README.md)

***

# Function: requestAPI()

> **requestAPI**(`userQuery`): `Promise`\<`boolean` \| `void`\>

Defined in: [src/services/AuthService.tsx:320](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/services/AuthService.tsx#L320)

Direct request to chat endpoint without streaming.

## Parameters

### userQuery

`string`

Message to send

## Returns

`Promise`\<`boolean` \| `void`\>

- On success: backend response body
 - On failure: `void` (and logs error)
