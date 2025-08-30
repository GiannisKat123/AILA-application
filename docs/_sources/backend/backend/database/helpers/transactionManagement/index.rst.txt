backend.database.helpers.transactionManagement
==============================================

.. py:module:: backend.database.helpers.transactionManagement

.. autoapi-nested-parse::

   Database Transaction Management
   ===============================

   This module provides utilities for managing SQLAlchemy database sessions
   using Python context variables and a decorator-based transaction wrapper.

   It allows seamless propagation of a database session across function calls
   without explicitly threading it through arguments. Functions can be safely
   decorated with ``@transactional`` to ensure they run inside a managed
   transactional context.

   Key features
   ~~~~~~~~~~~~
   - Context variable to store the active session
   - Implicit reuse of existing sessions
   - Automatic commit and rollback handling
   - Clean session closure after execution
   - Decorator pattern for function-level transaction management



Attributes
----------

.. autoapisummary::

   backend.database.helpers.transactionManagement.db_session_context


Functions
---------

.. autoapisummary::

   backend.database.helpers.transactionManagement.transactional


Module Contents
---------------

.. py:data:: db_session_context

   Context variable storing the active SQLAlchemy session.

.. py:function:: transactional(func)

   Decorator to wrap functions in a managed SQLAlchemy transaction.

   Ensures that:
   - If a session already exists in context, it is reused.
   - Otherwise, a new session is created, committed, and closed.
   - On errors, the session is rolled back and closed.

   :param func: The function to wrap. It must accept a `session` keyword argument.
   :type func: callable

   :returns: The wrapped function, executed within a database transaction.
   :rtype: callable

   .. rubric:: Example

   >>> @transactional
   ... def create_user(user: User, session=None):
   ...     session.add(user)
   ...     return user
   ...
   >>> new_user = create_user(User(...))


