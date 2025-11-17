from sqlalchemy.orm import Session
from ..entities.message import Message
from uuid import UUID
from sqlalchemy import desc,asc
from sqlalchemy.orm import aliased
from typing import List

class MessageDao:
    def createMessage(self,session:Session,Message:Message):
        try:
            session.add(Message)
            return Message
        except Exception as e:
            print(f"Error in MessagesDao.createMessage functionality, Error Message:{e}")
            raise e
        
    def fetcMessageById(self,session:Session,message_id:UUID) -> Message:
        try:
            message = session.query(Message).filter(Message.id == message_id).one_or_none()
            return message
        except Exception as e:
            print(f"Error in MessagesDao.fetcMessageById functionality, Error Message:{e}")
            raise e
        
    def fetchMessagesByConversationId(self,session:Session,conversation_id:UUID) -> List[Message]:
        try: 
            # messages = session.query(Message).filter(Message.conversation_id == conversation_id).order_by(desc(Message.date_created_on)).all()
            # return messages
            subq = (session.query(Message) 
                .filter(Message.conversation_id == conversation_id)
                .order_by(desc(Message.date_created_on))
                # .limit(5)
            ).subquery()
            
            recentMessages = aliased(Message, subq)

            messages = session.query(recentMessages).order_by(asc(recentMessages.date_created_on)).all()
            return messages
        except Exception as e:
            print(f"Error in MessagesDao.fetchMessagesByConversationId. Error Massage: {e}")
            raise e
        
    def updateMessageFeedback(self,session:Session,conversation_id:UUID, message_id:UUID,feedback:bool):
        try: 
            print(message_id,conversation_id)
            message = session.query(Message).filter(Message.id == message_id,Message.conversation_id==conversation_id).one_or_none()
            message.feedback = feedback
            session.commit()
        except Exception as e:
            print(f"Error in MessagesDao.updateMessageFeedback. Error Massage: {e}")
            raise e