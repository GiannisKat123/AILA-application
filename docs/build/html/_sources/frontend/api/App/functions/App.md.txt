[**vite-project v0.0.0**](../../README.md)

***

# Function: App()

> **App**(): `Element`

Defined in: [src/App.tsx:94](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/App.tsx#L94)

Root React component.

## Returns

`Element`

The top-level application component.

## Remarks

Defines the application’s routes using React Router v6 and renders
the global header banner via [Template](../../components/Template/functions/Template.md).

**Routing table:**
- `/login` → [Login](../../pages/Login/functions/Login.md) page
- `/register` → [Register](../../pages/Register/functions/Register.md) page
- `/chat` → [Chat](../../pages/Chat/functions/Chat.md) page (protected)
- `/` → Redirects to `/chat`
- `*` → Fallback to [Login](../../pages/Login/functions/Login.md) (could be replaced with 404)

## Example

```tsx
import { createRoot } from 'react-dom/client';
import App from './App';

createRoot(document.getElementById('root')!).render(<App />);
```
