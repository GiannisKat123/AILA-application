"""
Pydantic models used for request/response validation and API data contracts.

Each class defines the structure of data expected in API endpoints, ensuring
validation and automatic OpenAPI schema generation.
"""

from pydantic import BaseModel
from typing import List


class UserCredentials(BaseModel):
    """
    Represents login credentials for a user.

    Attributes
    ----------
    username : str
        The username of the user.
    password : str
        The plaintext password provided for authentication.
    """
    username: str
    password: str


class ConversationCreationDetails(BaseModel):
    """
    Represents details needed to create a new conversation.

    Attributes
    ----------
    username : str
        The username of the conversation owner.
    conversation_name : str
        A human-readable title for the conversation.
    """
    username: str
    conversation_name: str


class UpdateConversationDetails(BaseModel):
    """
    Represents details required to update an existing conversation.

    Attributes
    ----------
    conversation_name : str
        New name/title for the conversation.
    conversation_id : str
        Unique identifier of the conversation to update.
    """
    conversation_name: str
    conversation_id: str


class NewMessage(BaseModel):
    """
    Represents a new message to be created in a conversation.

    Attributes
    ----------
    feedback : bool | None
        Optional feedback flag (True/False, None if unset).
    id : str
        Unique identifier of the message.
    conversation_id : str
        The ID of the conversation the message belongs to.
    text : str
        The text content of the message.
    role : str
        The role of the sender (e.g., 'user', 'assistant', 'system').
    """
    feedback: bool | None
    id: str
    conversation_id: str
    text: str
    role: str


class UserOpenData(BaseModel):
    """
    Publicly shareable user data (non-sensitive).

    Attributes
    ----------
    email : str
        User's email address.
    username : str
        User's username.
    """
    email: str
    username: str


class Message(BaseModel):
    """
    Represents a message sent in an API request (e.g., chat interaction).

    Attributes
    ----------
    message : str
        The current message being sent.
    conversation_history : list[dict]
        History of previous messages in the conversation.
    """
    message: str
    conversation_history: List[dict]


class UserAuthentication(BaseModel):
    """
    Authentication response returned after login attempts.

    Attributes
    ----------
    authenticated : bool
        Whether the authentication was successful.
    detail : str
        Additional information or error message.
    user_details : UserCredentials | None
        User details if authenticated, otherwise None.
    """
    authenticated: bool
    detail: str
    user_details: UserCredentials | None


class UserData(BaseModel):
    """
    Represents data required to register a new user.

    Attributes
    ----------
    username : str
        Desired username.
    password : str
        Password chosen by the user.
    email : str
        Email address of the user.
    """
    username: str
    password: str
    email: str


class VerifCode(BaseModel):
    """
    Represents a request to verify a user's email.

    Attributes
    ----------
    username : str
        Username associated with the verification code.
    code : str
        Verification code provided by the user.
    """
    username: str
    code: str


class UserFeedback(BaseModel):
    """
    Represents feedback on a user message.

    Attributes
    ----------
    message_id : str
        The ID of the message being reviewed.
    conversation_id : str
        The conversation to which the message belongs.
    feedback : bool | None
        Feedback value (True=positive, False=negative, None=unset).
    """
    message_id: str
    conversation_id: str
    feedback: bool | None
