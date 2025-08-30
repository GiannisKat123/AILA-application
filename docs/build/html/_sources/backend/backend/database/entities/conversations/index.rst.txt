backend.database.entities.conversations
=======================================

.. py:module:: backend.database.entities.conversations

.. autoapi-nested-parse::

   Conversation ORM Model
   =======================

   The ``Conversation`` ORM model represents a user-owned conversation record stored
   in the ``conversation`` PostgreSQL table. It is implemented with SQLAlchemy
   2.0-style typing and PostgreSQL UUID columns.

   Key features
   ~~~~~~~~~~~~
   - PostgreSQL-native UUID primary key (``id``)
   - Human-readable name (``conversation_name``)
   - Foreign key to the owning user (``user_id`` → ``app_user.id``)
   - Timezone-aware ``last_updated`` timestamp (UTC)



Classes
-------

.. autoapisummary::

   backend.database.entities.conversations.Conversation


Module Contents
---------------

.. py:class:: Conversation(conversation_id: uuid.UUID, conversation_name: str, user_id: uuid.UUID, last_updated)

   Bases: :py:obj:`backend.database.config.connection_engine.declarativeBase`


   ORM model for the `conversation` table.
   Represents a conversation belonging to a specific user.

   .. attribute:: id

      Primary key. Unique identifier for the conversation.

      :type: UUID

   .. attribute:: conversation_name

      Human-readable name/title of the conversation.

      :type: str

   .. attribute:: user_id

      Foreign key reference to the `app_user` table (the owner of the conversation).

      :type: UUID

   .. attribute:: last_updated

      Timestamp of the last update to the conversation.
      Defaults to the current UTC time.

      :type: datetime


   .. py:attribute:: __tablename__
      :value: 'conversation'



   .. py:attribute:: id
      :type:  sqlalchemy.orm.Mapped[uuid.UUID]

      Primary key. UUID of the conversation.


   .. py:attribute:: conversation_name
      :type:  sqlalchemy.orm.Mapped[str]

      Name of the conversation (cannot be null).


   .. py:attribute:: user_id
      :type:  sqlalchemy.orm.Mapped[uuid.UUID]

      Foreign key reference to the `app_user` table (owner).


   .. py:attribute:: last_updated
      :type:  sqlalchemy.orm.Mapped[datetime.datetime]

      Timestamp when the conversation was last updated. Defaults to now (UTC).


   .. py:method:: __str__() -> str

      Return a human-readable string representation of the Conversation.

      :returns: A formatted string containing user ID, conversation name, and last updated timestamp.
      :rtype: str



