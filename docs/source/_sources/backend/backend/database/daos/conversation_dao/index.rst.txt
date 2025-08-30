backend.database.daos.conversation_dao
======================================

.. py:module:: backend.database.daos.conversation_dao

.. autoapi-nested-parse::

   Conversation DAO

   Purpose
   -------
   Provides a thin data-access layer for the `Conversation` ORM entity:
   - Create conversations
   - Query by user, by name, or both
   - Update `last_updated` and `conversation_name`

   Design
   ------
   - Requires an active SQLAlchemy `Session` supplied by the caller (no session
     creation inside the DAO). This keeps transaction boundaries in the service
     layer where they belong.
   - Uses straightforward ORM queries (`session.query(...).filter(...).all()`).
   - Update operations fetch the target row and mutate attributes, then `commit()`.

   Entity
   ------
   Conversation (imported from `backend.database.entities.conversations`)
   Expected columns used here:
   - id (UUID/string)
   - user_id (UUID)
   - conversation_name (str)
   - last_updated (timestamp/datetime or str)

   Usage
   -----
   .. code-block:: python

       from sqlalchemy.orm import Session
       from backend.database.connection_engine import connection_engine
       from backend.database.entities.conversations import Conversation
       from backend.database.daos.conversation_dao import ConversationDao  # wherever this file lives

       dao = ConversationDao()
       with Session(connection_engine) as session:
           # Create
           conv = Conversation(
               id=..., user_id=..., conversation_name="My Case", last_updated="2025-08-27T12:00:00Z"
           )
           dao.createConversation(session, conv)
           session.commit()  # Commit is the caller's responsibility after create

           # Read by user
           items = dao.fetchConversationByUserId(session, user_id=conv.user_id)

           # Read by name (global)
           items_by_name = dao.fetchConversationByConverastionName(session, "My Case")

           # Read by user + name
           items_by_user_and_name = dao.fetchConversationByUserIdAndConverastionName(
               session, conv.user_id, "My Case"
           )

           # Update timestamp
           dao.updateConversationByDate(session, conversation_id=str(conv.id), timestamp="2025-08-27T12:30:00Z")

           # Update name
           dao.updateConversationByName(session, conversation_id=str(conv.id), conversation_name="Renamed Case")

   Error Handling
   --------------
   - Methods catch generic `Exception`, log/print the error message, and re-raise.
   - `update*` methods use `.one()`, which raises `NoResultFound` or `MultipleResultsFound`
     if the target row count is not exactly one. Callers should be ready to handle these.



Classes
-------

.. autoapisummary::

   backend.database.daos.conversation_dao.ConversationDao


Module Contents
---------------

.. py:class:: ConversationDao

   Data Access Object (DAO) for managing Conversation entities.
   Provides CRUD operations on the `Conversation` table.


   .. py:method:: createConversation(session: sqlalchemy.orm.Session, conversation: backend.database.entities.conversations.Conversation)

      Create a new conversation record.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param conversation: Conversation entity instance to be added.
      :type conversation: Conversation

      :raises Exception: If the conversation cannot be created.



   .. py:method:: fetchConversationByUserId(session: sqlalchemy.orm.Session, user_id: uuid.UUID)

      Fetch all conversations belonging to a specific user,
      ordered by most recently updated.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param user_id: Unique identifier of the user.
      :type user_id: UUID

      :returns: List of conversations for the given user.
      :rtype: list[Conversation]

      :raises Exception: If the query fails.



   .. py:method:: fetchConversationByConverastionName(session: sqlalchemy.orm.Session, conversation_name: str)

      Fetch all conversations with a given conversation name.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param conversation_name: Name of the conversation.
      :type conversation_name: str

      :returns: List of matching conversations.
      :rtype: list[Conversation]

      :raises Exception: If the query fails.



   .. py:method:: fetchConversationByUserIdAndConverastionName(session: sqlalchemy.orm.Session, user_id: uuid.UUID, conversation_name: str)

      Fetch conversations for a user by both user ID and conversation name.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param user_id: Unique identifier of the user.
      :type user_id: UUID
      :param conversation_name: Name of the conversation.
      :type conversation_name: str

      :returns: List of matching conversations.
      :rtype: list[Conversation]

      :raises Exception: If the query fails.



   .. py:method:: updateConversationByDate(session: sqlalchemy.orm.Session, conversation_id: str, timestamp: str)

      Update the last updated timestamp of a conversation.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param conversation_id: Unique identifier of the conversation.
      :type conversation_id: str
      :param timestamp: New timestamp string to set (ISO format recommended).
      :type timestamp: str

      :raises Exception: If the update fails.



   .. py:method:: updateConversationByName(session: sqlalchemy.orm.Session, conversation_id: str, conversation_name: str)

      Update the name of a conversation.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param conversation_id: Unique identifier of the conversation.
      :type conversation_id: str
      :param conversation_name: New conversation name to assign.
      :type conversation_name: str

      :raises Exception: If the update fails.



