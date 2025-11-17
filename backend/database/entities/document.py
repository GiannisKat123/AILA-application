from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import ForeignKey, DateTime, Boolean
from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
from datetime import datetime
import uuid

class Document(declarativeBase):
    __tablename__ = 'Document'
    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key = True)
    document_theme_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('Document_Theme.id'),nullable=False)
    title: Mapped[str] = mapped_column(TEXT,nullable=False)
    content:Mapped[str] = mapped_column(TEXT,nullable=False)
    date_created: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now())

    def __init__(self,document_theme_id:UUID,title:str,content:str,date_created:datetime):
        self.id = uuid.uuid4()
        self.document_theme_id = document_theme_id
        self.title = title
        self.content = content
        self.date_created = datetime.fromisoformat(date_created) if isinstance(date_created, str) else date_created
    
    def __str__(self):
        return (f"Document: id:{self.id}, document_theme_id: {self.document_theme_id}, title: {self.title}, content: {self.content} ")

