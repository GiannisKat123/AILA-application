[**vite-project v0.0.0**](../../../README.md)

***

# Interface: AuthContextType

Defined in: [src/context/AuthContext.tsx:75](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L75)

Shape of the AuthContext — defines all state + actions

## Properties

### conversations

> **conversations**: `null` \| [`Conversations`](../../../models/Types/type-aliases/Conversations.md)[]

Defined in: [src/context/AuthContext.tsx:81](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L81)

List of all conversations for the user.

***

### createConversation()

> **createConversation**: (`conversation_name`, `username`) => `Promise`\<`undefined` \| [`Conversations`](../../../models/Types/type-aliases/Conversations.md)\>

Defined in: [src/context/AuthContext.tsx:85](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L85)

Create a new conversation.

#### Parameters

##### conversation\_name

`string`

##### username

`string`

#### Returns

`Promise`\<`undefined` \| [`Conversations`](../../../models/Types/type-aliases/Conversations.md)\>

***

### createMessage()

> **createMessage**: (`conversation_id`, `text`, `role`, `id`, `feedback`) => `Promise`\<`void`\>

Defined in: [src/context/AuthContext.tsx:87](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L87)

Create a new message in a conversation.

#### Parameters

##### conversation\_id

`string`

##### text

`string`

##### role

`string`

##### id

`string`

##### feedback

`null` | `boolean`

#### Returns

`Promise`\<`void`\>

***

### fetchConversations()

> **fetchConversations**: (`username`) => `Promise`\<`void`\>

Defined in: [src/context/AuthContext.tsx:95](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L95)

Fetch all conversations for the user.

#### Parameters

##### username

`string`

#### Returns

`Promise`\<`void`\>

***

### fetchUserMessages()

> **fetchUserMessages**: (`conversation_id`) => `Promise`\<`void`\>

Defined in: [src/context/AuthContext.tsx:89](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L89)

Fetch all messages for a conversation.

#### Parameters

##### conversation\_id

`string`

#### Returns

`Promise`\<`void`\>

***

### loading

> **loading**: `boolean`

Defined in: [src/context/AuthContext.tsx:83](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L83)

Loading state while verifying session.

***

### logoutUser()

> **logoutUser**: () => `Promise`\<`void`\>

Defined in: [src/context/AuthContext.tsx:93](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L93)

Logout the current user.

#### Returns

`Promise`\<`void`\>

***

### RegisterUser()

> **RegisterUser**: (`username`, `password`, `email`) => `Promise`\<`boolean` \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

Defined in: [src/context/AuthContext.tsx:97](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L97)

Register a new user.

#### Parameters

##### username

`string`

##### password

`string`

##### email

`string`

#### Returns

`Promise`\<`boolean` \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

***

### renameConversation()

> **renameConversation**: (`conversation_name`, `conversation_id`) => `Promise`\<`void` \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

Defined in: [src/context/AuthContext.tsx:105](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L105)

Rename a conversation.

#### Parameters

##### conversation\_name

`string`

##### conversation\_id

`string`

#### Returns

`Promise`\<`void` \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

***

### resendCode()

> **resendCode**: (`username`, `email`) => `Promise`\<`void`\>

Defined in: [src/context/AuthContext.tsx:101](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L101)

Resend a verification code.

#### Parameters

##### username

`string`

##### email

`string`

#### Returns

`Promise`\<`void`\>

***

### user

> **user**: `null` \| [`UserProfile`](../../../models/Types/type-aliases/UserProfile.md)

Defined in: [src/context/AuthContext.tsx:77](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L77)

Current logged-in user, or `null` if unauthenticated.

***

### userFeedback()

> **userFeedback**: (`message_id`, `conversation_id`, `feedback`) => `Promise`\<`void`\>

Defined in: [src/context/AuthContext.tsx:103](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L103)

Submit feedback on a message.

#### Parameters

##### message\_id

`string`

##### conversation\_id

`string`

##### feedback

`boolean`

#### Returns

`Promise`\<`void`\>

***

### userMessages

> **userMessages**: `null` \| [`Message`](../../../models/Types/type-aliases/Message.md)[]

Defined in: [src/context/AuthContext.tsx:79](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L79)

Messages in the active conversation.

***

### verifyCodeUser()

> **verifyCodeUser**: (`username`, `code`) => `Promise`\<`boolean` \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

Defined in: [src/context/AuthContext.tsx:99](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L99)

Verify a user with a code.

#### Parameters

##### username

`string`

##### code

`string`

#### Returns

`Promise`\<`boolean` \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

## Methods

### loginUser()

> **loginUser**(`username`, `password`): `Promise`\<`null` \| [`LoginAPIOutput`](../../../models/Types/type-aliases/LoginAPIOutput.md) \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>

Defined in: [src/context/AuthContext.tsx:91](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/context/AuthContext.tsx#L91)

Login a user.

#### Parameters

##### username

`string`

##### password

`string`

#### Returns

`Promise`\<`null` \| [`LoginAPIOutput`](../../../models/Types/type-aliases/LoginAPIOutput.md) \| [`ErrorMessage`](../../../models/Types/type-aliases/ErrorMessage.md)\>
