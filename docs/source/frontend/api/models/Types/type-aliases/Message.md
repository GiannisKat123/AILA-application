[**vite-project v0.0.0**](../../../README.md)

***

# Type Alias: Message

> **Message** = `object`

Defined in: [src/models/Types.ts:41](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/models/Types.ts#L41)

Represents a chat message inside a conversation.

## Properties

### feedback

> **feedback**: `boolean` \| `null`

Defined in: [src/models/Types.ts:42](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/models/Types.ts#L42)

User’s feedback on assistant’s reply.
- `true` → positive feedback
- `false` → negative feedback
- `null` → no feedback given

***

### id

> **id**: `string`

Defined in: [src/models/Types.ts:43](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/models/Types.ts#L43)

Unique identifier (UUID).

***

### message

> **message**: `string`

Defined in: [src/models/Types.ts:44](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/models/Types.ts#L44)

Message text.

***

### role

> **role**: `string`

Defined in: [src/models/Types.ts:46](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/models/Types.ts#L46)

Sender role ("user" | "assistant").

***

### timestamp

> **timestamp**: `string`

Defined in: [src/models/Types.ts:45](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/models/Types.ts#L45)

ISO-8601 formatted timestamp.
