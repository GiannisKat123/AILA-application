[**vite-project v0.0.0**](../README.md)

***

# App

Top-level React application component.

## Responsibilities
- Define the application routes using React Router v6.
- Protect sensitive routes (like `/chat`) behind authentication.
- Render shared layout (the `<Template />` banner) across all pages.

## Routing Table
- `/login`     → Login page
- `/register`  → Registration page (with verification flow)
- `/chat`      → Main Chat UI (requires authentication)
- `/`          → Redirects to `/chat`
- `*`          → Fallback to [Login](../pages/Login/functions/Login.md) (could be replaced with a 404)

## Components
- [Template](../components/Template/functions/Template.md): A static header/banner with project logos.
- PrivateRoute: Higher-order wrapper that guards protected pages.

## Functions

- [App](functions/App.md)

## References

### default

Renames and re-exports [App](functions/App.md)
