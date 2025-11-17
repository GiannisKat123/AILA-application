from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import TEXT, ForeignKey, DateTime
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
import uuid
from datetime import datetime, timezone

class Verification_Code(declarativeBase):
    __tablename__ = 'Verification_Code'
    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key=True)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),ForeignKey('App_User.id'),nullable=False)
    code: Mapped[str] = mapped_column(TEXT,nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now())

    def __init__(self,user_id:UUID,code:str,expires_at:datetime):
        self.id = uuid.uuid4()
        self.user_id = user_id
        self.code = code
        self.expires_at = expires_at

    def __str__(self):
        return (f"Verification_Code: user_id:{self.user_id}, code: {self.code}, time created: {self.expires_at}")