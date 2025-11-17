from sqlalchemy.orm import Session
from ..entities.session import SessionModel
import uuid
from sqlalchemy import asc
from typing import List

class SessionDao:
    def create(self,session:Session,ses:SessionModel):
        try:
            session.add(ses)
        except Exception as e:
            print(f"Error in SessionDao.create functionality, Error Message:{e}")
            raise e
        
    def fetchAll(self,session:Session) -> List[SessionModel]:
        try:
            return session.query(SessionModel).all()
        except Exception as e:
            print(f"Error in SessionDao.fetchAll functionality, Error Message:{e}")
            raise e

    def fetchByUserId(self,session:Session,user_id:uuid) -> List[SessionModel]:
        try:
            return session.query(SessionModel).filter(SessionModel.user_id == user_id).all()
        except Exception as e:
            print(f"Error in SessionDao.fetchByUserId functionality, Error Message:{e}")
            raise e
        
    def fetchByUserIdLastOne(self,session:Session,user_id:uuid) -> SessionModel:
        try:
            return session.query(SessionModel).filter(SessionModel.user_id == user_id).order_by(asc(SessionModel.time_created)).one()
        except Exception as e:
            print(f"Error in SessionDao.fetchByUserIdLastOne functionality, Error Message:{e}")
            raise e
        
    

