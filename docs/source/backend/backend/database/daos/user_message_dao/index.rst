backend.database.daos.user_message_dao
======================================

.. py:module:: backend.database.daos.user_message_dao

.. autoapi-nested-parse::

   User Messages DAO

   Purpose
   -------
   Data-access layer for the `UserMessage` ORM entity. Provides:
   - Message creation
   - Retrieval by conversation (chronological)
   - Feedback updates (thumbs up/down style boolean)

   Design
   ------
   - Requires an active SQLAlchemy `Session` provided by the caller.
   - Keeps business rules (auth, validation, rate limits) in higher layers.
   - Retrieval uses a subquery for "latest-first then re-order ascending" semantics;
     see "Performance & Alternatives" for simpler approaches.

   Entity (expected columns)
   -------------------------
   UserMessage:
   - id: UUID / primary key
   - conversation_id: UUID (FK to conversations)
   - role: str (e.g., "user", "assistant", "system")
   - message_text: str
   - feedback: bool | None
   - date_created_on: datetime (creation timestamp)

   Usage
   -----
   .. code-block:: python

       from sqlalchemy.orm import Session
       from backend.database.connection_engine import connection_engine
       from backend.database.entities.messages import UserMessage
       from backend.database.daos.user_messages_dao import UserMessagesDao

       dao = UserMessagesDao()
       with Session(connection_engine) as session:
           # Create a message (caller may choose to commit here or after a batch)
           msg = UserMessage(
               id=..., conversation_id=..., role="user", text="Acknowledge the Tribal Chief!",
           )
           dao.createMessage(session, msg)
           session.commit()

           # Fetch messages for a conversation (chronological)
           messages = dao.fetchMessagesByConversationId(session, conversation_id=msg.conversation_id)

           # Update feedback on a specific message
           dao.updateMessageFeedback(
               session,
               conversation_id=msg.conversation_id,
               message_id=msg.id,
               feedback=True,
           )

   Error Handling
   --------------
   - Methods catch generic `Exception`, print a message, and re-raise.
     Prefer structured logging (e.g., `logger.exception(...)`) over `print(...)`.
   - `updateMessageFeedback` uses `.one()` which raises:
     - `NoResultFound` if the message doesn’t exist or doesn’t belong to the conversation.
     - `MultipleResultsFound` if data integrity is violated (should not happen with proper PK/FK).



Classes
-------

.. autoapisummary::

   backend.database.daos.user_message_dao.UserMessagesDao


Module Contents
---------------

.. py:class:: UserMessagesDao

   Data Access Object (DAO) for managing User Messages.
   Provides methods to create, fetch, and update messages within conversations.


   .. py:method:: createMessage(session: sqlalchemy.orm.Session, userMessage: backend.database.entities.messages.UserMessage) -> backend.database.entities.messages.UserMessage

      Create a new user message record.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param userMessage: Message entity instance to be added.
      :type userMessage: UserMessage

      :returns: The message object that was added.
      :rtype: UserMessage

      :raises Exception: If the insert operation fails.



   .. py:method:: fetchMessagesByConversationId(session: sqlalchemy.orm.Session, conversation_id: uuid.UUID)

      Fetch all messages in a conversation, ordered by creation time (ascending).
      Internally, retrieves the latest messages first via a subquery,
      then re-orders them chronologically.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param conversation_id: Unique identifier of the conversation.
      :type conversation_id: UUID

      :returns: List of messages belonging to the specified conversation.
      :rtype: list[UserMessage]

      :raises Exception: If query fails.



   .. py:method:: updateMessageFeedback(session: sqlalchemy.orm.Session, conversation_id: uuid.UUID, message_id: uuid.UUID, feedback: bool)

      Update feedback status of a specific message within a conversation.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param conversation_id: Unique identifier of the conversation.
      :type conversation_id: UUID
      :param message_id: Unique identifier of the message.
      :type message_id: UUID
      :param feedback: New feedback value (e.g., True for positive, False for negative).
      :type feedback: bool

      :raises Exception: If update fails or message is not found.



