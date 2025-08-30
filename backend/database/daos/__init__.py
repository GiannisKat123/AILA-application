"""
The `daos` package provides the Data Access Layer for the application.

It is responsible for all interactions with the database entities,
encapsulating CRUD operations that support the core functionality
of the system. Each DAO operates on a specific entity and abstracts
away the direct SQLAlchemy queries, offering a cleaner API to the
service layer.

Contents
--------
- UserDao
    Handles user persistence:
    * Creates users with password hashing
    * Fetches users by username or email
    * Updates verification status and codes
    * Manages authentication/session tokens

- ConversationDao
    Manages conversation records:
    * Creates new conversations
    * Fetches conversations by user ID or name
    * Updates conversation name and last-updated timestamp

- UserMessagesDao
    Manages user message records:
    * Creates messages within a conversation
    * Fetches messages by conversation (chronological order)
    * Updates message feedback status
"""
