from pydantic import BaseModel
from typing import List

class UserCredentials(BaseModel):
    username:str
    password:str

class ConversationCreationDetails(BaseModel):
    username:str
    conversation_name:str

class UpdateConversationDetails(BaseModel):
    conversation_name:str
    conversation_id:str

class NewMessage(BaseModel):
    feedback: bool | None
    id:str
    conversation_id:str
    text:str
    role:str

class UserOpenData(BaseModel):
    email:str
    username:str

class Message(BaseModel):
    message:str
    conversation_history:List[dict]

class UserAuthentication(BaseModel):
    authenticated:bool
    detail:str
    user_details:UserCredentials|None

class UserData(BaseModel):
    username:str
    password:str
    email:str

class VerifCode(BaseModel):
    username:str
    code:str


class UserFeedback(BaseModel):
    message_id:str
    conversation_id:str
    feedback:bool | None