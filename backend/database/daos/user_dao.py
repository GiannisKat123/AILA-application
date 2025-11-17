from sqlalchemy.orm import Session
from ..entities.user import User
from backend.crypt.encrypt_decrypt import EncryptionDec
from typing import List

class UserDao:
    def createUser(self,session:Session,user_data:User):
        try:
            enc = EncryptionDec()
            user_data.password = enc.hash_password(text=user_data.password)
            session.add(user_data)
            return True
        except Exception as e:
            print(f"Error in UserDao.createUser functionality, Error Message:{e}")
            raise e
        
    def fetchById(self,session:Session,user_id:str) -> User:
        try:
            user = session.query(User).filter(User.id == user_id).one_or_none()
            return user
        except Exception as e:
            print(f"Error in UserDao.fetchById. Error Massage: {e}")
            raise e

    def fetchUser(self,session:Session,username:str) -> User:
        try: 
            user = session.query(User).filter(User.user_name==username).one_or_none()
            return user
        except Exception as e:
            print(f"Error in UserDao.fetchUser. Error Massage: {e}")
            raise e

    def fetchUserByEmail(self,session:Session,email:str) -> User:
        try: 
            users = session.query(User).filter(User.email==email).one_or_none()
            return users
        except Exception as e:
            print(f"Error in UserDao.fetchUserByEmail. Error Massage: {e}")
            raise e
        
    def updateVerified(self,session:Session,username:str,verified:bool):
        try:
            user = session.query(User).filter(User.user_name == username).one_or_none()
            user.verified = verified
            session.commit()
        except Exception as e:
            print(f"Error in UserDao.updateVerCode. Error Massage: {e}")
            raise e
        
    def fetchUserByRole(self,session:Session,role:str) -> List[User]:
        try:
            users = session.query(User).filter(User.role == role).all()
            return users
        except Exception as e:
            print(f"Error in UserDao.fetchUserByRole. Error Massage: {e}")
            raise e
