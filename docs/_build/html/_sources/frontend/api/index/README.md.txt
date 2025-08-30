[**vite-project v0.0.0**](../README.md)

***

# index

Frontend entrypoint for the AILA Chatbot Demo.

Responsibilities
----------------
- Bootstraps React (concurrent root via React 18).
- Wraps the app with:
  - <BrowserRouter> for client-side routing
  - <AuthProvider> to expose authentication & app state globally
- Applies global styles (Tailwind / index.css).

Notes
-----
- Ensure BrowserRouter is imported from 'react-router-dom' (NOT 'react-router').
  If you see navigation issues, switch:
    import { BrowserRouter } from 'react-router-dom';

## Example
```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
```
