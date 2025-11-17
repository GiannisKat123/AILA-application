from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import ForeignKey, DateTime, Boolean
from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
import uuid
from datetime import datetime, timezone

class Document_Feedback(declarativeBase):
    __tablename__ = 'Document_Feedback'
    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),primary_key = True)
    query_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('message_user.id'),nullable=False)
    negative_query_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('message_user.id'),nullable=False)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('App_User.id'),nullable=False)  
    document_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('Document.id'),nullable=False)
    context: Mapped[str] = mapped_column(TEXT,nullable=False)
    date_created_on: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now())

    def __init__(self,query_id:UUID,negative_id:UUID,user_id:UUID,document_id:str,context:str):
        self.id = uuid.uuid4()
        self.query_id = query_id
        self.negative_query_id = negative_id
        self.user_id = user_id
        self.document_id = document_id
        self.context = context
        self.date_created_on = datetime.now().isoformat()

    def __str__(self):
        return (f"Document_Feedback: id:{self.id}, query_id: {self.query_id}, negative_id: {self.negative_query_id}, user_id: {self.user_id}, doc name: {self.document_id}")

