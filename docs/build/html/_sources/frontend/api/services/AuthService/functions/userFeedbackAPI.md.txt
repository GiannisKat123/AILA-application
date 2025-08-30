[**vite-project v0.0.0**](../../../README.md)

***

# Function: userFeedbackAPI()

> **userFeedbackAPI**(`message_id`, `conversation_id`, `feedback`): `Promise`\<`undefined` \| `boolean`\>

Defined in: [src/services/AuthService.tsx:196](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/services/AuthService.tsx#L196)

Submit feedback for a specific assistant message.

## Parameters

### message\_id

`string`

Message UUID

### conversation\_id

`string`

Conversation UUID

### feedback

true = 👍, false = 👎, undefined = clear/reset

`undefined` | `boolean`

## Returns

`Promise`\<`undefined` \| `boolean`\>

- On success: `true`
 - On failure: `undefined` (and logs error)
