"""
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

"""

from backend.database.config.connection_engine import declarativeBase
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import ForeignKey, DateTime, Boolean, TEXT
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from datetime import datetime, timezone

class DocumentFeedback(declarativeBase):
    """
    ORM model for the `message` table.
    Represents a single message within a conversation.

    Attributes
    ----------
    id : UUID
        Primary key. Unique identifier for the message.
    conversation_id : UUID
        Foreign key reference to the `conversation` table.
    date_created_on : datetime
        Timestamp when the message was created.
    message_text : str
        Content of the message.
    role : str
        Role of the sender (e.g., "user", "assistant", "system").
    feedback : bool | None
        Optional feedback flag for the message (True/False). Default is None.
    """

    __tablename__ = 'document_feedback'

    id: Mapped[UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True
    )
    """Primary key. UUID of the message."""

    query_id: Mapped[UUID] = mapped_column(
        pgUUID(as_uuid=True), ForeignKey('message.id'), nullable=False
    )
    """Foreign key to the conversation this message belongs to."""

    negative_answer_id: Mapped[UUID] = mapped_column(
        pgUUID(as_uuid=True), ForeignKey('message.id'), nullable=False
    )

    doc_name: Mapped[str] = mapped_column(
        TEXT, nullable=False
    )

    doc_text: Mapped[str] = mapped_column(
        TEXT, nullable=False
    )

    context: Mapped[str] = mapped_column(
        TEXT, nullable=False
    )

    theme: Mapped[str] = mapped_column(
        TEXT, nullable=False
    )

    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    """Timestamp when the message was created. Defaults to current UTC time."""

    def __init__(
        self,
        doc_id:UUID,
        query_id: UUID,
        negative_answer_id: UUID,
        doc_name: str,
        doc_text: str,
        context: str,
        theme:str,
        date_created,
    ):
        """
        Initialize a new UserMessage object.

        Parameters
        ----------
        message_id : UUID
            Unique identifier of the message.
        conversation_id : UUID
            ID of the conversation this message belongs to.
        message : str
            The content of the message.
        date_created_on : datetime | str
            Timestamp when the message was created. Accepts datetime or ISO8601 string.
        role : str
            The role of the sender (user/assistant/system).
        feedback : bool | None, optional
            Feedback flag for the message (default is None).
        """
        self.id = doc_id
        self.query_id = query_id
        self.negative_answer_id = negative_answer_id
        self.doc_name = doc_name
        self.doc_text = doc_text
        self.context = context
        self.theme = theme
        self.date_created = date_created
        if isinstance(date_created, str):
            self.date_created = datetime.fromisoformat(date_created)
        else:
            self.date_created = date_created

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the message.

        Returns
        -------
        str
            A formatted string containing conversation ID, message text, role, and creation timestamp.
        """
        return (
            f"Conversation: id:{self.id}, "
            f"query_id: {self.query_id}, "
            f"negative_answer_id: {self.negative_answer_id}, "
            f"doc_name: {self.doc_name}"
        )
