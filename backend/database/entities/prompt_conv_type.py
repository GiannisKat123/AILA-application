from ..config.connection_engine import declarativeBase
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy import TEXT, ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
import uuid

class Prompt_Conv_Type(declarativeBase):
    __tablename__ = 'Prompt_To_Conversation_Type'
    conv_type_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),ForeignKey('Conversation_Type.id'),nullable=False,primary_key=True,)
    prompt_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True),ForeignKey('Prompt.id'),nullable=False,primary_key=True,)

    def __init__(self,conv_type_id:UUID,prompt_id:str=UUID):
        self.id = uuid.uuid4()
        self.conv_type_id = conv_type_id
        self.prompt_id = prompt_id

    def __str__(self):
        return (f"Prompt_Conv_Type: conv_type_id:{self.conv_type_id}, prompt_id: {self.prompt_id}")