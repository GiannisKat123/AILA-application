from sqlalchemy.orm import Session
from ..entities.conversations import Conversation
from uuid import UUID
from sqlalchemy import desc

class ConversationDao:
    def createConversation(self,session:Session,conversation:Conversation):
        try:
            session.add(conversation)
        except Exception as e:
            print(f"Error in ConversationDao.createMessage functionality, Error Message:{e}")
            raise e
        
    def fetchConversationByUserId(self,session:Session,user_id:UUID):
        try: 
            conversations = session.query(Conversation).filter(Conversation.user_id==user_id).order_by(desc(Conversation.last_updated)).all()
            return conversations
        except Exception as e:
            print(f"Error in ConversationDao.fetchMessages. Error Massage: {e}")
            raise e
        
    def fetchConversationByConverastionName(self,session:Session,conversation_name:str):
        try: 
            conversation = session.query(Conversation).filter(Conversation.conversation_name == conversation_name).all()
            return conversation
        except Exception as e:
            print(f"Error in ConversationDao.fetchMessages. Error Massage: {e}")
            raise e
    
    def fetchConversationByUserIdAndConverastionName(self,session:Session,user_id:UUID,conversation_name:str):
        try: 
            conversation = session.query(Conversation).filter(Conversation.user_id==user_id).filter(Conversation.conversation_name == conversation_name).all()
            return conversation
        except Exception as e:
            print(f"Error in ConversationDao.fetchMessages. Error Massage: {e}")
            raise e
        
    def updateConversationByDate(self,session:Session,conversation_name:str,timestamp:str):
        try:
            conversation = session.query(Conversation).filter(Conversation.conversation_name == conversation_name).one()
            conversation.last_updated = timestamp
        except Exception as e:
            print(f"Error in ConversationDao.updateConversationByDate. Error Massage: {e}")
            raise e