backend.database.daos.user_dao
==============================

.. py:module:: backend.database.daos.user_dao

.. autoapi-nested-parse::

   User DAO

   Purpose
   -------
   Thin data-access layer for the `User` ORM entity. Provides:
   - Creation with password hashing
   - Lookup by username or email
   - Token retrieval and updates
   - Verification status and verification-code updates

   Design
   ------
   - The DAO expects an active SQLAlchemy `Session` supplied by the caller.
   - Business logic (validation, authorization, transactions) should live in a
     higher-level service; the DAO focuses on persistence operations.
   - Passwords are hashed using `EncryptionDec.hash_password(...)` before insert.

   Entity (expected columns)
   -------------------------
   - id: uuid / primary key
   - user_name: str (unique)
   - email: str (unique)
   - password: str (hashed)
   - role : str
   - verified: bool
   - verification_code: str | None
   - code_created_on: datetime | None
   - session_id: str | None  (JWT or session token)

   Usage
   -----
   .. code-block:: python

       from sqlalchemy.orm import Session
       from backend.database.connection_engine import connection_engine
       from backend.database.entities.user import User
       from backend.database.daos.user_dao import UserDao  # adjust path as needed

       dao = UserDao()
       with Session(connection_engine) as session:
           # Create user (password will be hashed)
           u = User(user_name="roman", email="roman@tribalchief.com", password="Spear#123")
           dao.createUser(session, u)
           session.commit()  # caller controls commit here

           # Fetch by username
           users = dao.fetchUser(session, "roman")     # returns list[User], at most 1 due to limit
           # Fetch by email
           users2 = dao.fetchUserByEmail(session, "roman@tribalchief.com")

           # Update verification status
           dao.updateVerified(session, "roman")

           # Update verification code and timestamp
           from datetime import datetime, timezone
           dao.updateVerCode(session, "roman", code="123456", code_created_on=datetime.now(timezone.utc))

           # Update token (e.g., after login)
           dao.updateToken(session, users[0].id, token="jwt-or-session-token")

   Error Handling
   --------------
   - Each method catches generic `Exception`, prints a message, and re-raises.
     Consider replacing `print(...)` with structured logging (e.g., `logger.exception(...)`).
   - Methods using `.one()` can raise `NoResultFound` or `MultipleResultsFound`.
     Upstream code should be ready to handle these.

   Return Values
   -------------
   - createUser(...) -> bool
   - fetchUser(...) -> list[User] (at most one row due to limit(1))
   - fetchUserByEmail(...) -> list[User] (at most one row due to limit(1))
   - fetchUserToken(...) -> str (intended), but see "Caveats" below
   - updateVerified(...), updateVerCode(...), updateToken(...) -> None (commit inside)



Classes
-------

.. autoapisummary::

   backend.database.daos.user_dao.UserDao


Module Contents
---------------

.. py:class:: UserDao

   Data Access Object (DAO) for managing User entities.
   Provides methods for creating users, retrieving user data,
   and updating authentication/verification fields.


   .. py:method:: createUser(session: sqlalchemy.orm.Session, user_data: backend.database.entities.user.User) -> bool

      Create a new user in the database with a hashed password.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param user_data: User entity object containing user details.
      :type user_data: User

      :returns: True if user creation is successful.
      :rtype: bool

      :raises Exception: If hashing or insertion fails.



   .. py:method:: fetchUser(session: sqlalchemy.orm.Session, username: str)

      Fetch a user by username.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param username: The username of the user.
      :type username: str

      :returns: A list containing the matching user (at most one due to limit(1)).
      :rtype: list[User]

      :raises Exception: If query fails.



   .. py:method:: fetchUserByEmail(session: sqlalchemy.orm.Session, email: str)

      Fetch a user by email.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param email: Email address of the user.
      :type email: str

      :returns: A list containing the matching user (at most one due to limit(1)).
      :rtype: list[User]

      :raises Exception: If query fails.



   .. py:method:: fetchUserToken(session: sqlalchemy.orm.Session, username: str)

      Fetch the session token of a user by username.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param username: The username of the user.
      :type username: str

      :returns: The session token of the user.
      :rtype: str

      :raises Exception: If user does not exist or query fails.



   .. py:method:: updateVerified(session: sqlalchemy.orm.Session, username: str)

      Mark a user as verified.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param username: The username of the user.
      :type username: str

      :raises Exception: If user cannot be found or update fails.



   .. py:method:: updateVerCode(session: sqlalchemy.orm.Session, username: str, code: str, code_created_on)

      Update a user's verification code and creation timestamp.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param username: The username of the user.
      :type username: str
      :param code: The new verification code.
      :type code: str
      :param code_created_on: Timestamp when the code was generated.
      :type code_created_on: datetime

      :raises Exception: If update fails.



   .. py:method:: updateToken(session: sqlalchemy.orm.Session, user_id: uuid.UUID, token: str)

      Update a user's session token.

      :param session: Active SQLAlchemy session.
      :type session: Session
      :param user_id: Unique identifier of the user.
      :type user_id: uuid.UUID
      :param token: The new session token.
      :type token: str

      :raises Exception: If update fails.



