from sqlalchemy.orm import Session, aliased
from ..entities.messages import UserMessage
from uuid import UUID
from sqlalchemy import desc, asc

class UserMessagesDao:
    """
    Data Access Object (DAO) for managing User Messages.
    Provides methods to create, fetch, and update messages within conversations.
    """

    def createMessage(self, session: Session, userMessage: UserMessage) -> UserMessage:
        """
        Create a new user message record.

        Parameters
        ----------
        session : Session
            Active SQLAlchemy session.
        userMessage : UserMessage
            Message entity instance to be added.

        Returns
        -------
        UserMessage
            The message object that was added.

        Raises
        ------
        Exception
            If the insert operation fails.
        """
        try:
            session.add(userMessage)
            return userMessage
        except Exception as e:
            print(f"Error in UserMessagesDao.createMessage. Error Message: {e}")
            raise e

    def fetchMessagesByConversationId(self, session: Session, conversation_id: UUID):
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
            subq = (
                session.query(UserMessage)
                .filter(UserMessage.conversation_id == conversation_id)
                .order_by(desc(UserMessage.date_created_on))
                # Optional: uncomment limit for recent N messages
                # .limit(5)
            ).subquery()

            recentMessages = aliased(UserMessage, subq)

            messages = (
                session.query(recentMessages)
                .order_by(asc(recentMessages.date_created_on))
                .all()
            )
            return messages
        except Exception as e:
            print(f"Error in UserMessagesDao.fetchMessagesByConversationId. Error Message: {e}")
            raise e

    def updateMessageFeedback(self, session: Session, conversation_id: UUID, message_id: UUID, feedback: bool):
        """
        Update feedback status of a specific message within a conversation.

        Parameters
        ----------
        session : Session
            Active SQLAlchemy session.
        conversation_id : UUID
            Unique identifier of the conversation.
        message_id : UUID
            Unique identifier of the message.
        feedback : bool
            New feedback value (e.g., True for positive, False for negative).

        Raises
        ------
        Exception
            If update fails or message is not found.
        """
        try:
            message = (
                session.query(UserMessage)
                .filter(
                    UserMessage.id == message_id,
                    UserMessage.conversation_id == conversation_id,
                )
                .one()
            )
            message.feedback = feedback
            session.commit()
        except Exception as e:
            print(f"Error in UserMessagesDao.updateMessageFeedback. Error Message: {e}")
            raise e
