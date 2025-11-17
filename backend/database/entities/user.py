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
    __tablename__ = "App_User"
    id:Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key=True)
    user_name:Mapped[str] = mapped_column(TEXT,nullable=False)
    password:Mapped[str] = mapped_column(TEXT,nullable=False)
    role: Mapped[str] = mapped_column(TEXT,nullable=False)
    email: Mapped[str] = mapped_column(TEXT,nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean,nullable=False)
    AFM: Mapped[str] = mapped_column(TEXT,nullable=True)
    created_on: Mapped[datetime] = mapped_column(DateTime(timezone=False),default=datetime.now())

    def __init__(self,user_name:str,password:str,role:str,email:str,created_on:datetime,AFM:str=None):
        self.id = uuid.uuid4()
        self.user_name = user_name
        self.password = password
        self.role = role
        self.email = email
        self.verified = False
        self.created_on = datetime.fromisoformat(created_on) if isinstance(created_on, str) else created_on

    def __str__(self):
        return (f"Agent: id:{self.id}, username: {self.user_name}, password:{self.password}")
    
    