from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.mssql import DATETIME
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
from datetime import datetime, timezone

class UserMessage(declarativeBase):
    __tablename__ = 'message'
    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key = True)
    conversation_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('conversation.id'),nullable=False)
    date_created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    message_text: Mapped[str] = mapped_column(TEXT,nullable=False)
    role:Mapped[str] = mapped_column(TEXT,nullable=False)

    def __init__(self,message_id,conversation_id,message,date_created_on,role):
        self.id = message_id
        self.conversation_id = conversation_id
        self.message_text = message
        self.role = role
        if isinstance(date_created_on, str):
            self.date_created_on = datetime.fromisoformat(date_created_on)
        else:
            self.date_created_on = date_created_on

    def __str__(self):
        return (f"User: id:{self.user_id}, message: {self.message}, time_created: {self.date_created_on}")

