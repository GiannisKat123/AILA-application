/**
 * main.tsx / index.tsx
 * ============================================================
 * App bootstrap for AILA.
 *
 * What happens here:
 * - Create React 18 root
 * - Provide TanStack Query client for data fetching & caching
 * - Provide AuthProvider for global auth/conversation state
 * - Wire up React Router (BrowserRouter) for client-side navigation
 *
 * IMPORTANT:
 * - Use BrowserRouter from 'react-router-dom' (NOT 'react-router').
 * - Provider order:
 *     QueryClientProvider (network/cache)
 *       └── AuthProvider (auth state)
 *             └── BrowserRouter (routing context)
 *                   └── <App />
 */

import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";
import { BrowserRouter as Router } from "react-router-dom"; // ✅ correct package
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./context/AuthContext";

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
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
