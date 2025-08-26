from sqlalchemy.orm import Session
from ..entities.user import User
import uuid
from backend.crypt.encrypt_decrypt import EncryptionDec

class UserDao:
    """
    Data Access Object (DAO) for managing User entities.
    Provides methods for creating users, retrieving user data,
    and updating authentication/verification fields.
    """

    def createUser(self, session: Session, user_data: User) -> bool:
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
            enc = EncryptionDec()
            user_data.password = enc.hash_password(text=user_data.password)
            session.add(user_data)
            return True
        except Exception as e:
            print(f"Error in UserDao.createUser. Error Message: {e}")
            raise e

    def fetchUser(self, session: Session, username: str):
        """
        Fetch a user by username.

        Parameters
        ----------
        session : Session
            Active SQLAlchemy session.
        username : str
            The username of the user.

        Returns
        -------
        list[User]
            A list containing the matching user (at most one due to limit(1)).

        Raises
        ------
        Exception
            If query fails.
        """
        try:
            users = session.query(User).filter(User.user_name == username).limit(1).all()
            return users
        except Exception as e:
            print(f"Error in UserDao.fetchUser. Error Message: {e}")
            raise e

    def fetchUserByEmail(self, session: Session, email: str):
        """
        Fetch a user by email.

        Parameters
        ----------
        session : Session
            Active SQLAlchemy session.
        email : str
            Email address of the user.

        Returns
        -------
        list[User]
            A list containing the matching user (at most one due to limit(1)).

        Raises
        ------
        Exception
            If query fails.
        """
        try:
            users = session.query(User).filter(User.email == email).limit(1).all()
            return users
        except Exception as e:
            print(f"Error in UserDao.fetchUserByEmail. Error Message: {e}")
            raise e

    def fetchUserToken(self, session: Session, username: str):
        """
        Fetch the session token of a user by username.

        Parameters
        ----------
        session : Session
            Active SQLAlchemy session.
        username : str
            The username of the user.

        Returns
        -------
        str
            The session token of the user.

        Raises
        ------
        Exception
            If user does not exist or query fails.
        """
        try:
            users = session.query(User).filter(User.user_name == username)
            return users.session_id
        except Exception as e:
            print(f"Error in UserDao.fetchUserToken. Error Message: {e}")
            raise e

    def updateVerified(self, session: Session, username: str):
        """
        Mark a user as verified.

        Parameters
        ----------
        session : Session
            Active SQLAlchemy session.
        username : str
            The username of the user.

        Raises
        ------
        Exception
            If user cannot be found or update fails.
        """
        try:
            user = session.query(User).filter(User.user_name == username).one()
            user.verified = True
            session.commit()
        except Exception as e:
            print(f"Error in UserDao.updateVerified. Error Message: {e}")
            raise e

    def updateVerCode(self, session: Session, username: str, code: str, code_created_on):
        """
        Update a user's verification code and creation timestamp.

        Parameters
        ----------
        session : Session
            Active SQLAlchemy session.
        username : str
            The username of the user.
        code : str
            The new verification code.
        code_created_on : datetime
            Timestamp when the code was generated.

        Raises
        ------
        Exception
            If update fails.
        """
        try:
            user = session.query(User).filter(User.user_name == username.strip()).one()
            user.verification_code = code
            user.code_created_on = code_created_on
            session.commit()
        except Exception as e:
            print(f"Error in UserDao.updateVerCode. Error Message: {e}")
            raise e

    def updateToken(self, session: Session, user_id: uuid.UUID, token: str):
        """
        Update a user's session token.

        Parameters
        ----------
        session : Session
            Active SQLAlchemy session.
        user_id : uuid.UUID
            Unique identifier of the user.
        token : str
            The new session token.

        Raises
        ------
        Exception
            If update fails.
        """
        try:
            user = session.query(User).filter(User.id == user_id).one()
            user.session_id = token
            session.commit()
        except Exception as e:
            print(f"Error in UserDao.updateToken. Error Message: {e}")
            raise e
