from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import TEXT, ForeignKey, DateTime
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
import uuid
from datetime import datetime, timezone

class SessionModel(declarativeBase):
    __tablename__ = 'Session_creation'
    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key=True)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),ForeignKey('App_User.id'),nullable=False)
    session_token: Mapped[str] = mapped_column(TEXT,nullable=False)
    time_created:Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now())

    def __init__(self,user_id:UUID,session_token:str,time_created:datetime):
        self.id = uuid.uuid4()
        self.user_id = user_id
        self.session_token = session_token
        self.time_created = datetime.fromisoformat(time_created) if isinstance(time_created, str) else time_created

    def __str__(self):
        return (f"Session: user_id:{self.user_id}, session_token: {self.session_token}, datetime: {self.time_created}")