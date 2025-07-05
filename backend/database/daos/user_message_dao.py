from sqlalchemy.orm import Session
from ..entities.messages import UserMessage
from uuid import UUID
from sqlalchemy import desc,asc
from sqlalchemy.orm import aliased

class UserMessagesDao:
    def createMessage(self,session:Session,userMessage:UserMessage):
        try:
            session.add(userMessage)
            return userMessage
        except Exception as e:
            print(f"Error in UserMessagesDao.createMessage functionality, Error Message:{e}")
            raise e
        
    def fetchMessagesByConversationId(self,session:Session,conversation_id:UUID):
        try: 
            subq = (session.query(UserMessage) 
                .filter(UserMessage.conversation_id == conversation_id)
                .order_by(desc(UserMessage.date_created_on))
                # .limit(5)
            ).subquery()
            
            recentMessages = aliased(UserMessage, subq)

            messages = session.query(recentMessages).order_by(asc(recentMessages.date_created_on)).all()
            return messages
        except Exception as e:
            print(f"Error in UserMessagesDao.fetchMessages. Error Massage: {e}")
            raise e
        
    def updateMessageFeedback(self,session:Session,conversation_id:UUID, message_id:UUID,feedback:bool):
        try: 
            message = session.query(UserMessage).filter(UserMessage.id == message_id,UserMessage.conversation_id==conversation_id).one()
            message.feedback = feedback
            session.commit()
        except Exception as e:
            print(f"Error in UserMessagesDao.updateMessageFeedback. Error Massage: {e}")
            raise e