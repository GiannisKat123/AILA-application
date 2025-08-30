[**vite-project v0.0.0**](../../../README.md)

***

# Function: createMessageAPI()

> **createMessageAPI**(`conversation_id`, `text`, `role`, `id`, `feedback`): `Promise`\<`undefined` \| [`Message`](../../../models/Types/type-aliases/Message.md)\>

Defined in: [src/services/AuthService.tsx:245](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/services/AuthService.tsx#L245)

Create a new message within a conversation.

## Parameters

### conversation\_id

`string`

Conversation UUID

### text

`string`

Message content

### role

`string`

'user' | 'assistant'

### id

`string`

Client-generated UUID for the message

### feedback

Initial feedback (optional)

`null` | `boolean`

## Returns

`Promise`\<`undefined` \| [`Message`](../../../models/Types/type-aliases/Message.md)\>

- On success: `Message`
 - On failure: `undefined` (and logs error)
