from sqlalchemy.orm import Session
from ..entities.conversation import Conversation
from uuid import UUID
import uuid
from sqlalchemy import desc
from typing import List

class ConversationDao:
    def createConversation(self,session:Session,conversation:Conversation):
        try:
            session.add(conversation)
        except Exception as e:
            print(f"Error in ConversationDao.createConversation functionality, Error Message:{e}")
            raise e
        
    def fetchConversationByUserId(self,session:Session,user_id:UUID) -> List[Conversation]:
        try: 
            conversations = session.query(Conversation).filter(Conversation.user_id==user_id).order_by(desc(Conversation.last_updated)).all()
            return conversations
        except Exception as e:
            print(f"Error in ConversationDao.fetchConversationByUserId. Error Massage: {e}")
            raise e
        
    def fetchConversationByConversationName(self,session:Session,conversation_name:str) -> Conversation:
        try: 
            conversation = session.query(Conversation).filter(Conversation.name == conversation_name).one_or_none()
            return conversation
        except Exception as e:
            print(f"Error in ConversationDao.fetchConversationByConversationName. Error Massage: {e}")
            raise e
        
    def fetchConversationByConversationId(self,session:Session,conversation_id:UUID) -> Conversation:
        try: 
            conversation = session.query(Conversation).filter(Conversation.id == conversation_id).one_or_none()
            return conversation
        except Exception as e:
            print(f"Error in ConversationDao.fetchConversationByConversationId. Error Massage: {e}")
            raise e
    
    def fetchConversationByUserIdAndConverastionName(self,session:Session,user_id:UUID,conversation_name:str) -> Conversation:
        try: 
            conversation = session.query(Conversation).filter(Conversation.user_id==user_id).filter(Conversation.name == conversation_name).one_or_none()
            return conversation
        except Exception as e:
            print(f"Error in ConversationDao.fetchConversationByUserIdAndConverastionName. Error Massage: {e}")
            raise e
        
    def updateConversationByDate(self,session:Session,conversation_id:uuid,timestamp:str):
        try:
            conversation = session.query(Conversation).filter(Conversation.id == conversation_id).one_or_none()
            conversation.last_updated = timestamp
            session.commit()
        except Exception as e:
            print(f"Error in ConversationDao.updateConversationByDate. Error Massage: {e}")
            raise e
        
    def updateConversationByNameByUserId(self,session:Session,user_id:UUID,conversation_id:UUID,conversation_name:str):
        try:
            print(user_id,conversation_id,conversation_name)
            conversation = session.query(Conversation).filter(Conversation.user_id == user_id).filter(Conversation.id == conversation_id).one_or_none()
            conversation.name = conversation_name
            session.commit()
        except Exception as e:
            print(f"Error in ConversationDao.updateConversationByNameByUserId. Error Massage: {e}")
            raise e
    
    def fetchConversationByConvTypeIdandUserId(self,session:Session,conv_type_id:UUID,user_id:UUID) -> List[Conversation]:
        try: 
            conversations = session.query(Conversation).filter(Conversation.user_id==user_id).filter(Conversation.conv_type_id == conv_type_id).all()
            return conversations
        except Exception as e:
            print(f"Error in ConversationDao.fetchConversationByConvTypeIdandUserId. Error Massage: {e}")
            raise e
        

