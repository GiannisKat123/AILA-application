"""
The `entities` package defines the ORM models of the application,
representing the database tables as Python classes via SQLAlchemy.

These entity classes are the foundation of the persistence layer,
used by DAOs (`daos` package) to perform CRUD operations.

Contents
--------
- User
    Represents a registered user in the system.
    * Stores credentials (with hashed password)
    * Holds session token, role, and verification details
    * Tracks email verification code and timestamp

- Conversation
    Represents a conversation belonging to a user.
    * Stores conversation ID, name, and owner (user_id)
    * Tracks last updated timestamp

- UserMessage
    Represents a single message within a conversation.
    * Stores message text, role (user/assistant/system)
    * Records creation timestamp
    * Allows optional feedback (positive/negative/None)
"""
