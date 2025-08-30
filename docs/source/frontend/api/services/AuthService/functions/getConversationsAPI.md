[**vite-project v0.0.0**](../../../README.md)

***

# Function: getConversationsAPI()

> **getConversationsAPI**(`username`): `Promise`\<`undefined` \| [`Conversations`](../../../models/Types/type-aliases/Conversations.md)[]\>

Defined in: [src/services/AuthService.tsx:267](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/services/AuthService.tsx#L267)

Fetch all conversations for a user.

## Parameters

### username

`string`

Username whose conversations to fetch

## Returns

`Promise`\<`undefined` \| [`Conversations`](../../../models/Types/type-aliases/Conversations.md)[]\>

- On success: `Conversations[]`
 - On failure: `undefined` (and logs error)
