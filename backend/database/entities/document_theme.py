from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
import uuid

class Document_Theme(declarativeBase):
    __tablename__ = 'Document_Theme'
    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key = True)
    theme: Mapped[str] = mapped_column(TEXT,nullable=False,unique=True)
    description:Mapped[str] = mapped_column(TEXT,nullable=True)

    def __init__(self,theme:str,description:str=None):
        self.id = uuid.uuid4()
        self.theme = theme
        self.description = description

    def __str__(self):
        return (f"Document_Theme: theme:{self.theme}, description: {self.description}")

