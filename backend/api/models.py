from pydantic import BaseModel

class UserCredentials(BaseModel):
    username:str
    password:str

class ConversationCreationDetails(BaseModel):
    username:str
    conversation_name:str

class NewMessage(BaseModel):
    feedback: bool | None
    id:str
    conversation_name:str
    text:str
    role:str

class UserOpenData(BaseModel):
    email:str
    username:str

class Message(BaseModel):
    message:str

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