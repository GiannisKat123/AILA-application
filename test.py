from sqlalchemy.orm import Session
from backend.database.daos.user_dao import UserDao
from backend.database.entities.user import User
from backend.database.helpers.transactionManagement import transactional

from backend.database.daos.prompt_dao import PromptDao
from backend.database.entities.prompt import Prompt

from backend.database.daos.conversation_type_dao import ConversationTypeDao
from backend.database.entities.conversation_type import Conversation_Type

from backend.database.daos.prompt_conv_type_dao import PromptConvTypeDao
from backend.database.entities.prompt_conv_type import Prompt_Conv_Type
from backend.database.daos.document_theme_dao import DocumentThemeDao
from backend.database.core.funcs import create_document,create_document_theme,get_document_themes
import os


files = os.listdir(f'{os.getcwd()}/backend/evaluation/files')
for file in files:  
        themes = get_document_themes()
        if file not in themes: create_document_theme(theme=file,description=None)
        print(file)
        for f in os.listdir(f'{os.getcwd()}/backend/evaluation/files/{file}'):
                path = f'{os.getcwd()}/backend/evaluation/files/{file}' + f'/{f}'
                print(f)
                with open(path,'r',encoding='utf-8') as doc_file:
                    doc_text = doc_file.read()
                create_document(theme=file,doc_name=f,doc_text=doc_text)

# def main(session:Session,username:str):
#     user_dao = UserDao()
#     users = user_dao.fetchUser(session=session,username=username)
#     return users

# print(main(username='admin'))

# def updateVerCode(session:Session,username:str,code:str,code_created_on):
#     print(username,code,code_created_on)
#     user = session.query(User).filter(User.user_name == username).one()
#     print(user)

# updateVerCode(username='user1',code='',code_created_on='')


    


@transactional
def tester(session:Session):


        document_theme_dao = DocumentThemeDao()
        print(document_theme_dao.fetchDocumentThemes(session))
        # document_dao = DocumentDao()

        # files = os.listdir(f'{os.getcwd()}/backend/evaluation/original_files')

        # for file in files:
        #         doc_theme = Doc
        #         document_theme_dao.createTheme(session,)

        # ## Creation of Conversation Types
        # conv_type_dao = ConversationTypeDao()
        # # conv_type = Conversation_Type('lawsuit')
        # # conv_type_dao.createConversationType(session,conv_type)


        # prompt_dao = PromptDao()
        # text = """Welcome to the lawsuit creation tool.  
        #         In this conversation, I will guide you through creating a phishing complaint.  

        #         Please note: This is a demo tool, so kindly keep that in mind.  

        #         To draft a complete and legally sound criminal complaint for phishing, I will need some specific details from you. Please provide the following information:  

        #         1. **Your personal details** (full name, contact information).  
        #         2. **The accused’s details** (if known).  
        #         3. **A detailed description of the events** (how the phishing occurred, through which platform, amounts of money involved, etc.).  
        #         4. **A chronological timeline** of what happened.  
        #         5. **Any evidence you have** (messages, transaction receipts, screenshots, or other supporting documents).  

        #         Once you provide these details, I will generate a structured draft of your complaint."""

        # name = 'lawsuit_automated_message'
        # prompt = Prompt(name,text)
        # prompt_dao.createPrompt(session,prompt=prompt)

        # # normal_conv_id = conv_type_dao.fetchConversationTypeByName(session,'normal').id
        # lawsuit_conv_id = conv_type_dao.fetchConversationTypeByName(session,'lawsuit').id

        # prompt_conv_type_dao = PromptConvTypeDao()
        # # prompt_conv_type = Prompt_Conv_Type(normal_conv_id,prompt.id)
        # # prompt_conv_type_dao.create(session,prompt_conv_type)

        # prompt_conv_type = Prompt_Conv_Type(lawsuit_conv_id,prompt.id)
        # prompt_conv_type_dao.create(session,prompt_conv_type)


tester()