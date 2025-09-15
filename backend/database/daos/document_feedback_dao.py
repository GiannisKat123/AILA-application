from sqlalchemy.orm import Session
from backend.database.entities.document_feedback import DocumentFeedback
import uuid

class DocumentFeedbackDao:
    def createDocument(self, session: Session, document_feedback: DocumentFeedback) -> bool:
        """
        Create a new user in the database with a hashed password.

        Parameters
        ----------
        session : Session
            Active SQLAlchemy session.
        user_data : User
            User entity object containing user details.

        Returns
        -------
        bool
            True if user creation is successful.

        Raises
        ------
        Exception
            If hashing or insertion fails.
        """
        try:
            session.add(document_feedback)
            return True
        except Exception as e:
            print(f"Error in DocumentFeedbackDao.createDocument. Error Message: {e}")
            raise e

    def fetchDocs(self, session: Session):
        """
        Fetch all messages in a conversation, ordered by creation time (ascending).
        Internally, retrieves the latest messages first via a subquery,
        then re-orders them chronologically.

        Parameters
        ----------
        session : Session
            Active SQLAlchemy session.
        conversation_id : UUID
            Unique identifier of the conversation.

        Returns
        -------
        list[UserMessage]
            List of messages belonging to the specified conversation.

        Raises
        ------
        Exception
            If query fails.
        """
        try:
            all_docs = session.query(DocumentFeedback).all()
            return all_docs
        except Exception as e:
            print(f"Error in DocumentFeedbackDao.fetchDocs. Error Message: {e}")
            raise e