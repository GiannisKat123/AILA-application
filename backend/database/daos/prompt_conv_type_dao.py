from sqlalchemy.orm import Session
from ..entities.prompt_conv_type import Prompt_Conv_Type
import uuid

class PromptConvTypeDao:
    def create(self,session:Session,prompt_conv_type:Prompt_Conv_Type):
        try:
            session.add(prompt_conv_type)
            return True
        except Exception as e:
            print(f"Error in PromptConvTypeDao.create functionality, Error Message:{e}")
            raise e
        
    def fetchByPromptId(self,session:Session,prompt_id:uuid):
        try:
            return session.query(Prompt_Conv_Type).filter(Prompt_Conv_Type.prompt_id==prompt_id).all()
        except Exception as e:
            print(f"Error in PromptConvTypeDao.fetchByPromptId functionality, Error Message:{e}")
            raise e
        
    def fetchByConvTypeId(self,session:Session,conv_type_id:uuid):
        try:
            return session.query(Prompt_Conv_Type).filter(Prompt_Conv_Type.conv_type_id == conv_type_id).all()
        except Exception as e:
            print(f"Error in PromptConvTypeDao.fetchByConvTypeId functionality, Error Message:{e}")
            raise e
        
    def fetchAll(self,session:Session):
        try:
            return session.query(Prompt_Conv_Type).all()
        except Exception as e:
            print(f"Error in PromptConvTypeDao.fetchAll functionality, Error Message:{e}")
            raise e
        
    def deleteByConvTypeId(self,session:Session,conv_type_id:uuid) -> bool:
        try:
            session.query(Prompt_Conv_Type).filter(Prompt_Conv_Type.conv_type_id==conv_type_id).delete(synchronize_session=False)
            return True
        except Exception as e:
            print(f"Error in PromptConvTypeDao.deleteByConvTypeId functionality, Error Message:{e}")
            raise e