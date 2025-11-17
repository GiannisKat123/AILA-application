from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import ForeignKey, DateTime, Boolean
from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
from datetime import datetime
import uuid

class Message(declarativeBase):
    __tablename__ = 'message_user'
    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key = True)
    conversation_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('Conversation.id'),nullable=False)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('App_User.id'),nullable=False)
    text: Mapped[str] = mapped_column(TEXT,nullable=False)
    role:Mapped[str] = mapped_column(TEXT,nullable=False)
    date_created_on: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now())
    feedback: Mapped[bool] = mapped_column(Boolean,nullable=True)

    def __init__(self,conversation_id:UUID,user_id:UUID,message_text:str,date_created_on:datetime,role:str,feedback:bool=None):
        self.id = uuid.uuid4()
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.text = message_text
        self.role = role
        self.feedback = feedback
        self.date_created_on = datetime.fromisoformat(date_created_on) if isinstance(date_created_on, str) else date_created_on

    def __str__(self):
        return (f"Message: id:{self.id}, message: {self.text}, time_created: {self.date_created_on}")

