from sqlalchemy.orm import Session
from ..entities.user import User
import uuid
from backend.crypt.encrypt_decrypt import EncryptionDec

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
        
    def fetchUser(self,session:Session,username:str):
        try: 
            users = session.query(User).filter(User.user_name==username).limit(1).all()
            return users
        except Exception as e:
            print(f"Error in UserDao.fetchUser. Error Massage: {e}")
            raise e
        
    def fetchUserByEmail(self,session:Session,email:str):
        try: 
            users = session.query(User).filter(User.email==email).limit(1).all()
            return users
        except Exception as e:
            print(f"Error in UserDao.fetchUserByEmail. Error Massage: {e}")
            raise e
        
    def fetchUserToken(self,session:Session,username:str):
        try: 
            users = session.query(User).filter(User.user_name==username)
            return users.session_id
        except Exception as e:
            print(f"Error in UserDao.fetchUserToken. Error Massage: {e}")
            raise e

    def updateVerified(self,session:Session,username:str):
        try:
            user = session.query(User).filter(User.user_name == username).one()
            user.verified = True
            session.commit()
        except Exception as e:
            print(f"Error in UserDao.updateVerCode. Error Massage: {e}")
            raise e

    def updateVerCode(self,session:Session,username:str,code:str,code_created_on):
        try:
            user = session.query(User).filter(User.user_name == username.strip()).one()
            user.verification_code = code
            user.code_created_on = code_created_on
            session.commit()
        except Exception as e:
            print(f"Error in UserDao.updateVerCode. Error Massage: {e}")
            raise e


    def updateToken(self,session:Session,user_id:uuid.UUID,token:str):
        try:
            user = session.query(User).filter(User.id == user_id).one()
            user.session_id = token
            session.commit()
        except Exception as e:
            print(f"Error in UserDao.updateToken. Error Massage: {e}")
            raise e