[**vite-project v0.0.0**](../../../README.md)

***

# Function: Chat()

> **Chat**(): `Element`

Defined in: [src/pages/Chat.tsx:77](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/pages/Chat.tsx#L77)

Chat component — renders the main conversation interface.

## Returns

`Element`

## Remarks

This component is the core chat UI for AILA. It manages conversation state,
message streaming, feedback, and user interactions.

## Responsibilities
- Display a sidebar of conversations (with create, select, and rename).
- Render the chat viewport with user and assistant messages.
- Stream assistant responses from the backend in real time.
- Capture 👍 / 👎 feedback on assistant messages.
- Manage authentication lifecycle actions (logout).
- Provide mobile-friendly sidebar toggle and responsive layout.

## Props
None. This component consumes global state from [useAuth](../../../context/AuthContext/functions/useAuth.md).

## Returns
A React element representing the chat UI with sidebar + main conversation area.

## Example

```tsx
import { Chat } from "./pages/Chat";

<Route path="/chat" element={<Chat />} />
```
