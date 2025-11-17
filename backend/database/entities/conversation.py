from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.mssql import DATETIME
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import ForeignKey, DateTime, TEXT
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
from datetime import datetime, timezone
import uuid

class Conversation(declarativeBase):
    __tablename__ = 'Conversation'
    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key = True)
    name:Mapped[str] = mapped_column(TEXT,nullable=False)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('App_User.id'),nullable=False)
    created_on: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now())
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now())
    conv_type_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('Conversation_Type.id'),nullable=False)

    def __init__(self,conversation_name:str,user_id:UUID,created_on:datetime,last_updated:datetime,conv_type_id:UUID):
        self.id = uuid.uuid4()
        self.name = conversation_name
        self.user_id = user_id
        self.created_on = datetime.fromisoformat(created_on) if isinstance(created_on, str) else created_on
        self.last_updated = datetime.fromisoformat(last_updated) if isinstance(last_updated, str) else last_updated
        self.conv_type_id = conv_type_id

    def __str__(self):
        return (f"Conversation: id:{self.id}, conversation: {self.name}, time_created: {self.created_on}, type: {self.conv_type_id}")

