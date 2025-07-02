from pydantic import BaseModel

class UserCredentials(BaseModel):
    username:str
    password:str

class ConversationCreationDetails(BaseModel):
    username:str
    conversation_name:str

class NewMessage(BaseModel):
    conversation_name:str
    text:str
    role:str

class Message(BaseModel):
    message:str

class UserAuthentication(BaseModel):
    authenticated:bool
    detail:str
    user_details:UserCredentials|None