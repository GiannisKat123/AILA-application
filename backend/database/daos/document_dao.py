from sqlalchemy.orm import Session
from ..entities.document import Document
from uuid import UUID
from sqlalchemy import desc,asc
from sqlalchemy.orm import aliased
from typing import List

class DocumentDao:
    def createDocument(self,session:Session,Doc:Document):
        try:
            session.add(Doc)
            return Doc
        except Exception as e:
            print(f"Error in DocumentDao.createDocument functionality, Error Message:{e}")
            raise e
        
    def fetcDocumentById(self,session:Session,doc_id:UUID) -> Document:
        try:
            document = session.query(Document).filter(Document.id == doc_id).one_or_none()
            return document
        except Exception as e:
            print(f"Error in DocumentDao.fetcDocumentById functionality, Error Message:{e}")
            raise e
    
    def fetcDocumentByThemeId(self,session:Session,doc_theme_id:UUID) -> List[Document]:
        try:
            document = session.query(Document).filter(Document.document_theme_id == doc_theme_id).all()
            return document
        except Exception as e:
            print(f"Error in DocumentDao.fetcDocumentByThemeId functionality, Error Message:{e}")
            raise e
        
    def fetchByName(self,session:Session,name:str) -> Document:
        try:
            document = session.query(Document).filter(Document.title == name).one_or_none()
            return document
        except Exception as e:
            print(f"Error in DocumentDao.fetchByName functionality, Error Message:{e}")
            raise e