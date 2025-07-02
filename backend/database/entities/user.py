from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import VARCHAR
from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
import uuid

class User(declarativeBase):
    __tablename__ = "app_user"
    id:Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key=True)
    user_name:Mapped[str] = mapped_column(VARCHAR(255),nullable=False)
    password:Mapped[str] = mapped_column(TEXT,nullable=False)
    session_id: Mapped[str] = mapped_column(TEXT,nullable=False)
    role: Mapped[str] = mapped_column(TEXT,nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(255),nullable=False)

    def __init__(self,user_name,password,role,email):
        self.id = uuid.uuid4()
        self.user_name = user_name
        self.password = password
        self.role = role
        self.email = email

    def __str__(self):
        return (f"Agent: id:{self.id}, username: {self.user_name}, password:{self.password}")
    
    