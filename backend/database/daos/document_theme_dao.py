from sqlalchemy.orm import Session
from ..entities.document_theme import Document_Theme
from uuid import UUID
from typing import List

class DocumentThemeDao:
    def createTheme(self,session:Session,DocumentTheme:Document_Theme):
        try:
            session.add(DocumentTheme)
            return DocumentTheme
        except Exception as e:
            print(f"Error in DocuemntThemeDao.createTheme functionality, Error Message:{e}")
            raise e
        
    def fetchDocumentThemes(self,session:Session) -> List[Document_Theme]:
        try:
            themes = session.query(Document_Theme).all()
            print(themes)
            return themes
        except Exception as e:
            print(f"Error in DocuemntThemeDao.fetchDocumentThemes functionality, Error Message:{e}")
            raise e

    def fetcDocumentThemeByTheme(self,session:Session,theme:str) -> Document_Theme:
        try:
            theme = session.query(Document_Theme).filter(Document_Theme.theme == theme).one_or_none()
            return theme
        except Exception as e:
            print(f"Error in DocuemntThemeDao.fetcDocumentThemeByTheme functionality, Error Message:{e}")
            raise e
        