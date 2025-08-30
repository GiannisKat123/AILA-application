backend.api.fast_api
====================

.. py:module:: backend.api.fast_api

.. autoapi-nested-parse::

   FastAPI Router: Authentication, User Management, Conversations, and Chat API

   This module defines the HTTP API endpoints exposed by the backend. It handles:
   - User login, registration, verification, and logout
   - Conversation creation, update, retrieval
   - Messaging (new messages, fetch messages)
   - Feedback on messages
   - Integration with the LLM pipeline for legal Q&A

   Each endpoint validates input via Pydantic models and returns structured responses.



Attributes
----------

.. autoapisummary::

   backend.api.fast_api.router


Functions
---------

.. autoapisummary::

   backend.api.fast_api.login
   backend.api.fast_api.register
   backend.api.fast_api.verify
   backend.api.fast_api.resend_code
   backend.api.fast_api.new_conversation
   backend.api.fast_api.update_conversation
   backend.api.fast_api.new_message
   backend.api.fast_api.get_user_conversations
   backend.api.fast_api.get_messages
   backend.api.fast_api.user_feedback
   backend.api.fast_api.get_user
   backend.api.fast_api.chat_endpoint
   backend.api.fast_api.logout


Module Contents
---------------

.. py:data:: router

   Creates the FastAPI router in which we define its routes

.. py:function:: login(data: backend.api.models.UserCredentials, response: fastapi.Response)
   :async:


   Authenticate a user and set JWT as cookie.

   Request Body
   ------------
   UserCredentials {username: str, password: str}

   :returns: {'user_details': {...}} if successful.
   :rtype: dict

   :raises HTTPException 401: If authentication fails.


.. py:function:: register(data: backend.api.models.UserData)
   :async:


   Register a new user account.

   Request Body
   ------------
   UserData {username: str, password: str, email: str}

   :returns: True if registration successful.
   :rtype: bool

   :raises HTTPException 401: If username or email already exists, or invalid password.


.. py:function:: verify(data: backend.api.models.VerifCode)
   :async:


   Verify a user's email using a code.

   Request Body
   ------------
   VerifCode {username: str, code: str}

   :returns: True if verification successful.
   :rtype: bool

   :raises HTTPException 401: If code expired or mismatched.


.. py:function:: resend_code(data: backend.api.models.UserOpenData)
   :async:


   Resend a verification code to a user's email.

   Request Body
   ------------
   UserOpenData {username: str, email: str}

   :returns: True if code resent.
   :rtype: bool


.. py:function:: new_conversation(data: backend.api.models.ConversationCreationDetails)
   :async:


   Create a new conversation.

   Request Body
   ------------
   ConversationCreationDetails {username: str, conversation_name: str}

   :returns: {'conversation_name': str, 'conversation_id': UUID}
   :rtype: dict


.. py:function:: update_conversation(data: backend.api.models.UpdateConversationDetails)
   :async:


   Update the name of an existing conversation.

   Request Body
   ------------
   UpdateConversationDetails {conversation_id: str, conversation_name: str}

   :returns: True if update successful.
   :rtype: bool


.. py:function:: new_message(data: backend.api.models.NewMessage)
   :async:


   Create a new message in a conversation.

   Request Body
   ------------
   NewMessage {id: str, conversation_id: str, text: str, role: str, feedback: bool|None}

   :returns: {'id': str, 'message': str, 'timestamp': str, 'role': str}
   :rtype: dict


.. py:function:: get_user_conversations(token: str = Cookie(None), username: str = '')
   :async:


   Fetch all conversations for a given user.

   Request Body
   ----------------
   username : str
       The username whose conversations to fetch.

   :returns: [{'conversation_name': str, 'conversation_id': UUID}, ...]
   :rtype: list[dict]


.. py:function:: get_messages(token: str = Cookie(None), conversation_id: str = '')
   :async:


   Fetch messages for a given conversation.

   Request Body
   ----------------
   conversation_id : str
       ID of the conversation.

   :returns: List of messages in ascending timestamp order.
   :rtype: list[dict]


.. py:function:: user_feedback(data: backend.api.models.UserFeedback)

   Submit feedback for a user message.

   Request Body
   ------------
   UserFeedback {message_id: str, conversation_id: str, feedback: bool|None}


.. py:function:: get_user(token: str = Cookie(None))

   Retrieve user details from JWT token.

   :returns: {'username': str, 'email': str, 'verified': bool|None}
   :rtype: dict


.. py:function:: chat_endpoint(request_data: backend.api.models.Message, request: fastapi.Request)
   :async:


   Main chat endpoint integrating with the LLM pipeline.

   Request Body
   ------------
   Message {message: str, conversation_history: list[dict]}

   :returns: * *StreamingResponse* -- Streamed LLM-generated response (Server-Sent Events).
             * *JSONResponse* -- If the query is rejected as unsafe or non-legal.


.. py:function:: logout(response: fastapi.Response)
   :async:


   Logout user by clearing JWT cookie.

   :returns: True if logout successful.
   :rtype: bool


