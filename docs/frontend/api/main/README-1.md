[**vite-project v0.0.0**](../README.md)

***

# main

## Remarks

Application bootstrap for **AILA**. Creates the React 18 root and wires the
top‑level providers:

What happens here:
- Create React 18 root
- Provide TanStack Query client for data fetching & caching
- Provide AuthProvider for global auth/conversation state
- Wire up React Router (BrowserRouter) for client-side navigation

 * IMPORTANT:
- Use BrowserRouter from 'react-router-dom' (NOT 'react-router').
- Provider order:
    QueryClientProvider (network/cache)
      └── AuthProvider (auth state)
            └── BrowserRouter (routing context)
                  └── <App />

1. [QueryClientProvider](https://tanstack.com/query/latest/docs/framework/react/reference/QueryClientProvider) — network & cache layer (TanStack Query)
2. [AuthProvider](../context/AuthContext/functions/AuthProvider.md) — authentication and conversation state
3. BrowserRouter — client‑side routing context
4. [App](../App/functions/App.md) — application shell and routes

**Provider order** matters: Query/cache → Auth → Router → App.

## Example

```tsx
const queryClient = new QueryClient();

createRoot(document.getElementById('root')!).render(
 <React.StrictMode>
   <QueryClientProvider client={queryClient}>
     <AuthProvider>
       <Router>
         <App />
       </Router>
     </AuthProvider>
   </QueryClientProvider>
</React.StrictMode>
);
```
