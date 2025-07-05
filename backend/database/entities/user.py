from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import VARCHAR, Boolean
from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime

class User(declarativeBase):
    __tablename__ = "app_user"
    id:Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key=True)
    user_name:Mapped[str] = mapped_column(VARCHAR(255),nullable=False)
    password:Mapped[str] = mapped_column(TEXT,nullable=False)
    session_id: Mapped[str] = mapped_column(TEXT,nullable=False)
    role: Mapped[str] = mapped_column(TEXT,nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(255),nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean,nullable=False)
    verification_code: Mapped[str] = mapped_column(TEXT,nullable=False)
    code_created_on : Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    def __init__(self,user_name,password,role,email,verification_code,date_created_on,session_id):
        self.id = uuid.uuid4()
        self.session_id = session_id
        self.user_name = user_name
        self.password = password
        self.role = role
        self.email = email
        self.verified = False
        self.verification_code = verification_code
        if isinstance(date_created_on, str):
            self.code_created_on = datetime.fromisoformat(date_created_on)
        else:
            self.code_created_on = date_created_on

    def __str__(self):
        return (f"Agent: id:{self.id}, username: {self.user_name}, password:{self.password}")
    
    