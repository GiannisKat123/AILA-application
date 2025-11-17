from sqlalchemy.orm import Session
from ..entities.conversation_type import Conversation_Type
from typing import List

class ConversationTypeDao:
    def createConversationType(self,session:Session,conv_type:Conversation_Type):
        try:
            session.add(conv_type)
        except Exception as e:
            print(f"Error in ConversationTypeDao.createConversationType functionality, Error Message:{e}")
            raise e
        
    def fetchConversationType(self,session:Session) -> List[Conversation_Type]:
        try:
            conversation_types = session.query(Conversation_Type).all()
            return conversation_types
        except Exception as e:
            print(f"Error in ConversationTypeDao.fetchConversationType functionality, Error Message:{e}")
            raise e
        
    def fetchConversationTypeByName(self,session:Session,name:str) -> Conversation_Type:
        try:
            print(name)
            conversation_type = session.query(Conversation_Type).filter(Conversation_Type.name==name).one_or_none()
            return conversation_type
        except Exception as e:
            print(f"Error in ConversationTypeDao.fetchConversationTypeByName functionality, Error Message:{e}")
            raise e