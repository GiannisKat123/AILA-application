backend.main
============

.. py:module:: backend.main

.. autoapi-nested-parse::

   FastAPI application bootstrap with:

   - Lifespan-managed initialization of the LLM pipeline (indexes + reranker client)

   - CORS configured for the frontend

   - Authenticated WebSocket endpoint (cookie-based token)

   - Static file serving for built frontend

   - Catch-all route to support React Router


   Environment contract (from `settings`):

   - INIT_MODE: if 'runtime', preload indexes & reranker during app startup.

   - FRONTEND_URL: allowed CORS origin.



Attributes
----------

.. autoapisummary::

   backend.main.app
   backend.main.logger
   backend.main.url


Functions
---------

.. autoapisummary::

   backend.main.lifespan
   backend.main.websocket_endpoint
   backend.main.serve_react_app


Module Contents
---------------

.. py:function:: lifespan(app: fastapi.FastAPI)
   :async:


   App lifespan manager.

   .. rubric:: Notes

   - On startup (before yielding):
       * If INIT_MODE == 'runtime':
           - Build vector indexes (top_k=10).
           - Load Cohere client + reranker (retry loop until available).
           - Construct and initialize `LLM_Pipeline`, attach to `app.state`.
   - On shutdown (after yielding):
       * If a pipeline was created, call `shutdown()` to release resources.


.. py:data:: app

   Instatiates a FastAPI application object
   The lifespan=lifespan argument registers a custom startup/shutdown lifecycle manager that:

       - On startup: initializes the LLM pipeline (indexes + reranker) if INIT_MODE == 'runtime'.

       - On shutdown: gracefully releases pipeline resources.

.. py:data:: logger

   Logger instance for capturing and emitting Uvicorn server logs.

.. py:data:: url

   The allowed frontend origin (URL) used for CORS configuration.
   This value comes from application settings and represents the domain that is permitted to interact with the backend via cross-origin requests.

.. py:function:: websocket_endpoint(websocket: fastapi.WebSocket, token: str = Cookie(None))
   :async:


   Authenticated WebSocket endpoint.

   Auth
   ----
   - Expects a cookie named `token`.
   - `verify_token(token)` returns a username on success; otherwise connection is closed.

   Protocol
   --------
   - Upon connect: accepts and greets the authenticated user.
   - Echo loop: echoes back text messages.
   - On disconnect: logs a simple message (replace with real cleanup if needed).

   Close Codes
   -----------
   - 1008: Policy Violation (used when auth fails).


.. py:function:: serve_react_app(full_path: str = '')
   :async:


   Serve the frontend's index.html for all non-API routes to support client-side routing.


