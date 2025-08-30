[**vite-project v0.0.0**](../../../README.md)

***

# Function: createConversationAPI()

> **createConversationAPI**(`conversation_name`, `username`): `Promise`\<`undefined` \| [`Conversations`](../../../models/Types/type-aliases/Conversations.md)\>

Defined in: [src/services/AuthService.tsx:219](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/services/AuthService.tsx#L219)

Create a new conversation for the user.

## Parameters

### conversation\_name

`string`

Initial title

### username

`string`

Owner username

## Returns

`Promise`\<`undefined` \| [`Conversations`](../../../models/Types/type-aliases/Conversations.md)\>

- On success: `{ conversation_id, conversation_name }`
 - On failure: `undefined` (and logs error)
