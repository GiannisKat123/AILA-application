[**vite-project v0.0.0**](../../../README.md)

***

# Function: renameConversationAPI()

> **renameConversationAPI**(`conversation_name`, `conversation_id`): `Promise`\<`boolean` \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

Defined in: [src/services/AuthService.tsx:91](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/services/AuthService.tsx#L91)

Rename a conversation title.

## Parameters

### conversation\_name

`string`

New title

### conversation\_id

`string`

Conversation UUID

## Returns

`Promise`\<`boolean` \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

- On success: `true`
 - On failure: `{ error_message: string }`
