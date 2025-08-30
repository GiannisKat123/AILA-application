backend.database.entities.messages
==================================

.. py:module:: backend.database.entities.messages

.. autoapi-nested-parse::

   UserMessage ORM Model
   =====================

   The ``UserMessage`` ORM model represents a single message record within a
   conversation. Each message is tied to a ``Conversation`` entity via a
   foreign key and may optionally carry user feedback.

   Key features
   ~~~~~~~~~~~~
   - PostgreSQL-native UUID primary key (``id``)
   - Foreign key reference to ``conversation.id`` (``conversation_id``)
   - Timezone-aware ``date_created_on`` timestamp (UTC)
   - Message text content (``message_text``)
   - Sender role indicator (``role``)
   - Optional feedback flag (``feedback``)



Classes
-------

.. autoapisummary::

   backend.database.entities.messages.UserMessage


Module Contents
---------------

.. py:class:: UserMessage(message_id: uuid.UUID, conversation_id: uuid.UUID, message: str, date_created_on, role: str, feedback: bool | None = None)

   Bases: :py:obj:`backend.database.config.connection_engine.declarativeBase`


   ORM model for the `message` table.
   Represents a single message within a conversation.

   .. attribute:: id

      Primary key. Unique identifier for the message.

      :type: UUID

   .. attribute:: conversation_id

      Foreign key reference to the `conversation` table.

      :type: UUID

   .. attribute:: date_created_on

      Timestamp when the message was created.

      :type: datetime

   .. attribute:: message_text

      Content of the message.

      :type: str

   .. attribute:: role

      Role of the sender (e.g., "user", "assistant", "system").

      :type: str

   .. attribute:: feedback

      Optional feedback flag for the message (True/False). Default is None.

      :type: bool | None


   .. py:attribute:: __tablename__
      :value: 'message'



   .. py:attribute:: id
      :type:  sqlalchemy.orm.Mapped[uuid.UUID]

      Primary key. UUID of the message.


   .. py:attribute:: conversation_id
      :type:  sqlalchemy.orm.Mapped[uuid.UUID]

      Foreign key to the conversation this message belongs to.


   .. py:attribute:: date_created_on
      :type:  sqlalchemy.orm.Mapped[datetime.datetime]

      Timestamp when the message was created. Defaults to current UTC time.


   .. py:attribute:: message_text
      :type:  sqlalchemy.orm.Mapped[str]

      Text content of the message (cannot be null).


   .. py:attribute:: role
      :type:  sqlalchemy.orm.Mapped[str]

      Role of the message sender (e.g., user, assistant, system).


   .. py:attribute:: feedback
      :type:  sqlalchemy.orm.Mapped[bool]

      Optional feedback flag (True = positive, False = negative, None = not set).


   .. py:method:: __str__() -> str

      Return a human-readable string representation of the message.

      :returns: A formatted string containing conversation ID, message text, role, and creation timestamp.
      :rtype: str



