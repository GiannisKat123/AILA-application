/**
 * App.tsx
 * ============================================================
 * Top-level React application component.
 *
 * Responsibilities
 * ----------------
 * - Define the application routes using React Router v6.
 * - Protect sensitive routes (like `/chat`) behind authentication.
 * - Render shared layout (the <Template /> banner) across all pages.
 *
 * Routing Table
 * -------------
 * - `/login`     → Login page
 * - `/register`  → Registration page (with verification flow)
 * - `/chat`      → Main Chat UI (requires authentication)
 * - `/`          → Redirects to `/chat`
 * - `*`          → Fallback to <Login /> (could be replaced with a 404)
 *
 * Components
 * ----------
 * - Template: A static header/banner with project logos.
 * - PrivateRoute: Higher-order wrapper that guards protected pages.
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Chat from './pages/Chat';
import Register from './pages/Register';
import { useAuth } from './context/AuthContext';
import type { JSX } from 'react';
import { Template } from './components/Template';

/**
 * PrivateRoute
 * ------------------------------------------------------------
 * Wraps around routes that require authentication.
 *
 * Logic:
 * 1. Waits until the AuthContext finishes loading.
 * 2. If user exists AND user.verified === true → grant access.
 * 3. Otherwise → redirect to `/login`.
 *
 * @param children - The page component to render if access is granted.
 */
function PrivateRoute({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();

  if (loading) {
    // While verifying cookie/session with backend
    return <div>Loading...</div>;
  }

  // Debug output (can be removed in production)
  console.log(user);

  return user && user.verified === true
    ? children
    : <Navigate to='/login' replace />;
}

/**
 * App
 * ------------------------------------------------------------
 * Root component that defines routing and layout.
 *
 * - Displays the <Template /> at the top (logo/banner).
 * - Configures routes for login, register, chat, etc.
 * - Ensures chat is protected by authentication.
 */
function App() {
  return (
    <div>
      {/* Global banner visible on all routes */}
      <Template />

      {/* Define routes */}
      <Routes>
        {/* Public routes */}
        <Route path='/login' element={<Login />} />
        <Route path='/register' element={<Register />} />

        {/* Protected route */}
        <Route path='/chat' element={<PrivateRoute><Chat /></PrivateRoute>} />

        {/* Redirects & fallbacks */}
        <Route path='/' element={<Navigate to='/chat' />} />
        <Route path="*" element={<Login />} /> 
        {/* TODO: Replace with a proper 404 Not Found page */}
      </Routes>
    </div>
  );
}

export default App;
