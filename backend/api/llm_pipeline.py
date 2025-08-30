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
    """
    username: str
    """The username of the user"""
    password: str
    """The plaintext password provided for authentication."""

class ConversationCreationDetails(BaseModel):
    """
    Represents details needed to create a new conversation.
    """
    username: str
    """The username of the conversation owner."""
    conversation_name: str
    """A human-readable title for the conversation."""

class UpdateConversationDetails(BaseModel):
    """
    Represents details required to update an existing conversation.
    """
    conversation_name: str
    """New name/title for the conversation."""
    conversation_id: str
    """Unique identifier of the conversation to update."""

class NewMessage(BaseModel):
    """
    Represents a new message to be created in a conversation.
    """
    feedback: bool | None
    """Optional feedback flag (True/False, None if unset)."""
    id: str
    """Unique identifier of the message."""
    conversation_id: str
    """The ID of the conversation the message belongs to."""
    text: str
    """The text content of the message."""
    role: str
    """The role of the sender (e.g., 'user', 'assistant', 'system')."""


class UserOpenData(BaseModel):
    """
    Publicly shareable user data (non-sensitive).
    """
    email: str
    """User's email address."""
    username: str
    """User's username."""


class Message(BaseModel):
    """
    Represents a message sent in an API request (e.g., chat interaction).
    """
    message: str
    """The current message being sent."""
    conversation_history: List[dict]
    """History of previous messages in the conversation."""


class UserAuthentication(BaseModel):
    """
    Authentication response returned after login attempts.
    """
    authenticated: bool
    """Whether the authentication was successful."""
    detail: str
    """Additional information or error message."""
    user_details: UserCredentials | None
    """User details if authenticated, otherwise None."""


class UserData(BaseModel):
    """
    Represents data required to register a new user.
    """
    username: str
    """Desired username."""
    password: str
    """Password chosen by the user."""
    email: str
    """Email address of the user."""


class VerifCode(BaseModel):
    """
    Represents a request to verify a user's email.
    """
    username: str
    """Username associated with the verification code."""
    code: str
    """Verification code provided by the user."""


class UserFeedback(BaseModel):
    """
    Represents feedback on a user message.
    """
    message_id: str
    """The ID of the message being reviewed."""
    conversation_id: str
    """The conversation to which the message belongs."""
    feedback: bool | None
    """Feedback value (True=positive, False=negative, None=unset)."""
