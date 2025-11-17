from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
import uuid

class Prompt(declarativeBase):
    __tablename__ = "Prompt"
    id:Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key=True)
    name:Mapped[str] = mapped_column(TEXT,nullable=False)
    description:Mapped[str] = mapped_column(TEXT,nullable=False)

    def __init__(self,name:str,description:str=None):
        self.id = uuid.uuid4()
        self.name = name
        self.description = description

    def __str__(self):
        return (f"Prompt: id:{self.id}, name: {self.name}, description:{self.description}")
    