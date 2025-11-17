from sqlalchemy.orm import Session
from ..entities.verification_code import Verification_Code
import uuid
from sqlalchemy import asc,desc

class VerificationCodeDao:
    def create(self,session:Session,verification_code:Verification_Code):
        try:
            session.add(verification_code)
        except Exception as e:
            print(f"Error in VerificationCodeDao.create functionality, Error Message:{e}")
            raise e
        
    def fetchAll(self,session:Session):
        try:
            return session.query(Verification_Code).all()
        except Exception as e:
            print(f"Error in VerificationCodeDao.fetchAll functionality, Error Message:{e}")
            raise e

    def fetchByUserId(self,session:Session,user_id:uuid):
        try:
            return session.query(Verification_Code).filter(Verification_Code.user_id == user_id).all()
        except Exception as e:
            print(f"Error in VerificationCodeDao.fetchByUserId functionality, Error Message:{e}")
            raise e
        
    def fetchByUserIdLastOne(self,session:Session,user_id:uuid):
        try:
            codes = session.query(Verification_Code).filter(Verification_Code.user_id == user_id).order_by(desc(Verification_Code.expires_at)).all()
            if len(codes) == 0: return None
            else: return codes[0]
        except Exception as e:
            print(f"Error in VerificationCodeDao.fetchByUserIdLastOne functionality, Error Message:{e}")
            raise e
    
    
        