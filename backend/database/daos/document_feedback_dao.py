from sqlalchemy.orm import Session
from ..entities.document_feedback import Document_Feedback

class DocumentFeedbackDao:
    def createDocument(self,session:Session,document_feedback:Document_Feedback) -> bool:
        try:
            session.add(document_feedback)
            return True
        except Exception as e:
            print(f"Error in DocumentFeedbackDao.createDocument functionality, Error Message:{e}")
            raise e
        
    def fetchDocsFeedback(self,session:Session):
        try:
            docs = session.query(Document_Feedback).all()
            return docs
        except Exception as e:
            print(f"Error in DocumentFeedbackDao.fetchDocsFeedback functionality, Error Message:{e}")
            raise e
        
        