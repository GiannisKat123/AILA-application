[**vite-project v0.0.0**](../../../README.md)

***

# Function: getUserMessagesAPI()

> **getUserMessagesAPI**(`conversation_id`): `Promise`\<`undefined` \| [`Message`](../../../models/Types/type-aliases/Message.md)[]\>

Defined in: [src/services/AuthService.tsx:292](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/services/AuthService.tsx#L292)

Fetch all messages for a conversation.

## Parameters

### conversation\_id

`string`

Conversation UUID

## Returns

`Promise`\<`undefined` \| [`Message`](../../../models/Types/type-aliases/Message.md)[]\>

- On success: `Message[]`
 - On failure: throws Axios error (caller should handle)
