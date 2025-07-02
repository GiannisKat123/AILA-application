from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.mssql import DATETIME
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy import VARCHAR
from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
from datetime import datetime, timezone

class Conversation(declarativeBase):
    __tablename__ = 'conversation'
    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key = True)
    conversation_name:Mapped[str] = mapped_column(TEXT,nullable=False)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('app_user.id'),nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    def __init__(self,conversation_id,conversation_name,user_id,last_updated):
        self.id = conversation_id
        self.conversation_name = conversation_name
        self.user_id = user_id
        if isinstance(last_updated, str):
            self.last_updated = datetime.fromisoformat(last_updated)
        else:
            self.last_updated = last_updated

    def __str__(self):
        return (f"User: id:{self.user_id}, conversation: {self.conversation_name}, time_created: {self.last_updated}")

