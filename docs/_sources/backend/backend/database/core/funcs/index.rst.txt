backend.database.core.funcs
===========================

.. py:module:: backend.database.core.funcs

.. autoapi-nested-parse::

   Service-layer operations for authentication, conversations, and messages.

   All functions are wrapped with the `@transactional` decorator, which manages
   SQLAlchemy sessions and transactions automatically. Each function accepts (and
   uses) an injected `session: Session` provided by the decorator.

   This module provides high-level operations that orchestrate DAO calls and
   auxiliary services (encryption, email).



Functions
---------

.. autoapisummary::

   backend.database.core.funcs.login_user
   backend.database.core.funcs.check_create_user_instance
   backend.database.core.funcs.send_verification_code
   backend.database.core.funcs.check_verification_code
   backend.database.core.funcs.resend_ver_code
   backend.database.core.funcs.set_feedback
   backend.database.core.funcs.create_conversation
   backend.database.core.funcs.update_conv
   backend.database.core.funcs.create_message
   backend.database.core.funcs.update_token
   backend.database.core.funcs.get_token
   backend.database.core.funcs.get_user_messages
   backend.database.core.funcs.get_conversations


Module Contents
---------------

.. py:function:: login_user(session: sqlalchemy.orm.Session, username: str, password: str) -> backend.api.models.UserAuthentication

   Authenticate a user by username and password.

   :param session: Active SQLAlchemy session (injected by @transactional).
   :type session: Session
   :param username: Username to authenticate.
   :type username: str
   :param password: Plaintext password to verify.
   :type password: str

   :returns:

             A dict-like structure with:
               - authenticated (bool): True if credentials are valid.
               - detail (str): Error or info message.
               - user_details (dict | None): On success: {username, email, verified}; on failure may contain partial info.
   :rtype: UserAuthentication

   .. rubric:: Notes

   - Uses EncryptionDec.check_passwords for constant-time verification.
   - If the username does not exist, returns authenticated=False with a message.


.. py:function:: check_create_user_instance(session: sqlalchemy.orm.Session, username: str, password: str, email: str)

   Validate uniqueness, validate password policy, create a new user, and send a verification code.

   :param session: Active SQLAlchemy session (injected by @transactional).
   :type session: Session
   :param username: Desired username (must be unique).
   :type username: str
   :param password: Plaintext password to be validated and hashed at DAO level.
   :type password: str
   :param email: Email address (must be unique).
   :type email: str

   :returns:

             - On success: {'res': True, 'detail': <verification_code>}

             - On failure: {'res': False, 'detail': <reason>}
   :rtype: dict

   .. rubric:: Notes

   - Checks for existing username and email.
   - Validates password via `EncryptionDec.is_valid_password`.
   - Creates `User` with a generated verification code.
   - Sends the verification code via email.


.. py:function:: send_verification_code(email: str, code: str) -> None

   Send a verification code to the given email using Gmail SMTP.

   :param email: Recipient email address.
   :type email: str
   :param code: Verification code to send.
   :type code: str

   .. rubric:: Notes

   - Uses `settings.SENDER_EMAIL` and `settings.APP_PASSWORD` for SMTP auth.
   - Sends plain-text email via `smtp.gmail.com:587` with STARTTLS.
   - Exceptions are propagated to the caller.


.. py:function:: check_verification_code(session: sqlalchemy.orm.Session, username: str, user_code: str)

   Verify a user's email by checking their verification code and its expiry.

   :param session: Active SQLAlchemy session (injected by @transactional).
   :type session: Session
   :param username: Username whose code is being verified.
   :type username: str
   :param user_code: Code provided by the user.
   :type user_code: str

   :returns:

             - {'res': True, 'detail': ''} if verified.

             - {'res': False, 'detail': <reason>} if expired or mismatch.
   :rtype: dict

   .. rubric:: Notes

   - Code expires in 2 minutes from `user.code_created_on`.


.. py:function:: resend_ver_code(session: sqlalchemy.orm.Session, username: str, email: str) -> None

   Generate and send a new verification code for a user.

   :param session: Active SQLAlchemy session (injected by @transactional).
   :type session: Session
   :param username: Username to regenerate the code for.
   :type username: str
   :param email: Destination email address.
   :type email: str

   :raises Exception: Propagates any errors from DAO update or SMTP send.


.. py:function:: set_feedback(session: sqlalchemy.orm.Session, message_id: str, conversation_id: str, feedback: bool | None = None) -> None

   Set feedback flag on a user message.

   :param session: Active SQLAlchemy session (injected by @transactional).
   :type session: Session
   :param message_id: ID of the message to update.
   :type message_id: str
   :param conversation_id: ID of the conversation the message belongs to (validated in DAO).
   :type conversation_id: str
   :param feedback: Feedback value to set (True/False). Default is None.
   :type feedback: bool | None, optional


.. py:function:: create_conversation(session: sqlalchemy.orm.Session, username: str, conversation_name: str)

   Create a new conversation for a given user.

   :param session: Active SQLAlchemy session (injected by @transactional).
   :type session: Session
   :param username: Owner's username.
   :type username: str
   :param conversation_name: Human-readable name/title for the conversation.
   :type conversation_name: str

   :returns: {'conversation_name': <str>, 'conversation_id': <UUID>}
   :rtype: dict


.. py:function:: update_conv(session: sqlalchemy.orm.Session, conversation_id: str, conversation_name: str) -> None

   Update the name/title of an existing conversation.

   :param session: Active SQLAlchemy session (injected by @transactional).
   :type session: Session
   :param conversation_id: ID of the conversation to update.
   :type conversation_id: str
   :param conversation_name: New name for the conversation.
   :type conversation_name: str


.. py:function:: create_message(session: sqlalchemy.orm.Session, conversation_id: str, text: str, role: str, id: str, feedback: bool | None = None)

   Create a new message within a conversation and update the conversation's last_updated timestamp.

   :param session: Active SQLAlchemy session (injected by @transactional).
   :type session: Session
   :param conversation_id: ID of the parent conversation.
   :type conversation_id: str
   :param text: Message body/content.
   :type text: str
   :param role: Sender role (e.g., 'user', 'assistant', 'system').
   :type role: str
   :param id: Message ID to assign (UUID as string).
   :type id: str
   :param feedback: Optional feedback flag. Default: None.
   :type feedback: bool | None, optional

   :returns: {'id': <UUID>, 'message': <str>, 'timestamp': <datetime>, 'role': <str>}
   :rtype: dict


.. py:function:: update_token(session: sqlalchemy.orm.Session, username: str, token: str) -> None

   Update a user's session token.

   :param session: Active SQLAlchemy session (injected by @transactional).
   :type session: Session
   :param username: Username whose token should be updated.
   :type username: str
   :param token: New session token value.
   :type token: str


.. py:function:: get_token(session: sqlalchemy.orm.Session, username: str) -> str | None

   Retrieve the stored session token for a user.

   :param session: Active SQLAlchemy session (injected by @transactional).
   :type session: Session
   :param username: Username of the user.
   :type username: str

   :returns: The session token if present; otherwise None.
   :rtype: str | None


.. py:function:: get_user_messages(session: sqlalchemy.orm.Session, conversation_id: str) -> list[dict]

   List all messages for a conversation, formatted for API responses.

   :param session: Active SQLAlchemy session (injected by @transactional).
   :type session: Session
   :param conversation_id: ID of the conversation.
   :type conversation_id: str

   :returns: Each item: {'id', 'message', 'timestamp', 'role', 'feedback'}
             Returns an empty list if no messages are found.
   :rtype: list[dict]


.. py:function:: get_conversations(session: sqlalchemy.orm.Session, username: str) -> list[dict]

   List all conversations for a user.

   :param session: Active SQLAlchemy session (injected by @transactional).
   :type session: Session
   :param username: Owner's username.
   :type username: str

   :returns: Each item: {'conversation_name': <str>, 'conversation_id': <UUID>}
   :rtype: list[dict]


