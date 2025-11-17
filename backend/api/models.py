from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import Field, HttpUrl

class UserCredentials(BaseModel):
    username:str
    password:str

class UserDataReg(BaseModel):
    username:str
    password:str
    email:str
    role:str

class UserData(BaseModel):
    username:str
    email:str
    role:str

class UserAuthentication(BaseModel):
    authenticated:bool
    detail:str
    user_details:UserCredentials|None

class DefaultRes(BaseModel):
    res:bool
    detail:str

class ConversationType(BaseModel):
    conversation_name:str
    conversation_id: str
    conversation_type:str

class MessageType(BaseModel):
    id: str
    message: str
    timestamp: datetime
    role: str

class DocumentFeedbackDetails(BaseModel):
    username:str
    query_id: str
    negative_answer_id:str
    doc_name:str
    doc_text:str
    context:str
    theme:str
    
class VerifyUser(BaseModel):
    username:str
    verification_code:str    

class ConversationCreationDetails(BaseModel):
    username:str
    conversation_name:str
    conversation_type:str

class UpdateConversation(BaseModel):
    username:str
    conversation_id:str
    conversation_name:str

class Message(BaseModel):
    message_id:Optional[str] = None
    username:str
    conversation_id:str
    text:str
    role:str
    feedback:Optional[bool] = None

class UserMessage(BaseModel):
    message:str
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    web_search_tool: bool
    conversation_type:str
    conversation_id:str

class FileRec(BaseModel):
    """Metadata for an uploaded/stored file."""
    original: str = Field(..., description="Original filename as provided by the client.", example="report.pdf")
    path: str = Field(..., description="Server-side storage path or key.", example="/uploads/2025/09/report-1234.pdf")
    mime: str = Field(..., description="MIME type of the file.", example="application/pdf")
    public_url: Optional[HttpUrl] = Field(
        None,
        description="Publicly accessible URL if served via CDN/static hosting.",
        example="https://cdn.example.com/uploads/report-1234.pdf"
    )
