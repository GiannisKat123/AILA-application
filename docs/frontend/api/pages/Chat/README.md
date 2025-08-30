[**vite-project v0.0.0**](../../README.md)

***

# pages/Chat

## Remarks

The main chat UI for **AILA**. Provides:
- Conversation list (create, select, inline rename)
- Streaming chat with backend (`/request` endpoint)
- Persistence via AuthContextType
- Per‑message feedback (👍/👎)
- Responsive sidebar (mobile overlay)

**Data Flow**
1. On mount → fetch user’s conversations.
2. Auto‑select first conversation & fetch messages.
3. Local `messages` mirror context `userMessages` for real‑time patching.
4. On submit:
- Append user + placeholder assistant messages.
- Stream tokens and patch assistant message.
- Persist messages and refresh conversation.

Accessibility
-------------
- Uses semantic buttons & aria-friendly state updates.

Styling
-------
- TailwindCSS for layout & theming.
- lucide-react icons (User, Bot, Menu, X).
- Framer Motion for subtle entrance animation on greeting.

## Example

```tsx
import Chat from './pages/Chat';
<Route path="/chat" element={<Chat />} />
```

## Functions

- [Chat](functions/Chat.md)

## References

### default

Renames and re-exports [Chat](functions/Chat.md)
