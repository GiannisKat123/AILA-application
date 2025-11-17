from sqlalchemy.orm import Session
from ..entities.prompt import Prompt
import uuid

class PromptDao:
    def createPrompt(self,session:Session,prompt:Prompt):
        try:
            session.add(prompt)
            return True
        except Exception as e:
            print(f"Error in PromptDao.createPrompt functionality, Error Message:{e}")
            raise e
        
    def fetchPrompts(self,session:Session):
        try:
            prompts = session.query(Prompt).all()
            return prompts
        except Exception as e:
            print(f"Error in PromptDao.fetchPrompts functionality, Error Message:{e}")
            raise e
        
    def updatePrompt(self,session:Session,prompt_id:uuid,name:str,description:str):
        try:
            prompt = session.query(Prompt).filter(Prompt.id == prompt_id).one_or_none()
            prompt.name = name
            prompt.description = description
            session.commit()
        except Exception as e:
            print(f"Error in PromptDao.updatePrompt functionality, Error Message:{e}")
            raise e 
        
    def fetchPromptByName(self,session:Session,name:str):
        try:
            prompt = session.query(Prompt).filter(Prompt.name==name).all()[0]
            return prompt
        except Exception as e:
            print(f"Error in PromptDao.fetchPromptByName functionality, Error Message:{e}")
            raise e