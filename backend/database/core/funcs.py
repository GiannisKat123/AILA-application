from ..helpers.transactionManagement import transactional
from sqlalchemy.orm import Session
import uuid
from backend.database.daos.user_dao import UserDao
from backend.database.daos.conversation_dao import ConversationDao
from backend.database.daos.message_dao import MessageDao
from backend.database.daos.verification_code_dao import VerificationCodeDao
from backend.database.daos.conversation_type_dao import ConversationTypeDao
from backend.database.daos.session_dao import SessionDao
from backend.database.daos.document_feedback_dao import DocumentFeedbackDao
from backend.database.daos.prompt_dao import PromptDao
from backend.database.daos.document_dao import DocumentDao
from backend.database.daos.document_theme_dao import DocumentThemeDao

from backend.crypt.encrypt_decrypt import EncryptionDec
from backend.database.entities.message import Message
from backend.database.entities.conversation import Conversation
from backend.database.entities.verification_code import Verification_Code
from backend.database.entities.user import User
from backend.database.entities.session import SessionModel
from backend.database.entities.document_feedback import Document_Feedback
from backend.database.entities.document import Document
from backend.database.entities.document_theme import Document_Theme

from backend.api.models import UserAuthentication, DefaultRes, ConversationType, MessageType, DocumentFeedbackDetails
from datetime import datetime
from backend.database.config.config import settings
import smtplib
from email.mime.text import MIMEText
from typing import List
from datetime import timedelta

user_dao = UserDao()
verif_dao = VerificationCodeDao()
enc = EncryptionDec()
message_dao = MessageDao()
conversation_dao = ConversationDao()
conv_type_dao = ConversationTypeDao()
session_dao = SessionDao()
document_feedback_dao = DocumentFeedbackDao()
prompt_dao = PromptDao()
document_dao = DocumentDao()
document_theme_dao = DocumentThemeDao()

@transactional
def login_user(session:Session,username:str,password:str) -> UserAuthentication:
    user = user_dao.fetchUser(session,username)
    if user is None:
        return {
            'authenticated':False,
            'detail':'No user was found with that username',
            'user_details':None
        }
    else:
        if enc.check_passwords(password,user.password):
            return {
                'authenticated':True,
                'detail':'',
                'user_details':{'username':user.user_name,'email':user.email, 'verified': user.verified, 'role':user.role},
            }
        else:
            return {
                'authenticated':False,
                'detail':'Password is wrong',
                'user_details':{'username':user.user_name,'email':user.email},
            }

@transactional
def create_user_instance(session:Session, username:str, password:str, email:str, role:str) -> DefaultRes:
    user_in_database = user_dao.fetchUser(session=session,username=username)
    user_email_in_database = user_dao.fetchUserByEmail(session=session,email=email)
    print(username,password,email)
    if user_in_database is not None:
        print({'res':False,'detail':'User already exists'})
        return {'res':False,'detail':'User already exists'}
    elif user_email_in_database is not None:
        print({'res':False,'detail':'Email already exists'})
        return {'res':False,'detail':'Email already exists'}
    elif enc.is_valid_password(password):
        user = User(user_name = username, password = password, role = role, email = email, created_on = datetime.now().isoformat(), AFM = None)
        res = user_dao.createUser(session=session,user_data=user)
        send_ver_code(user=user)
        if res: return {'res':True, 'detail':''}
        else: return {'res':False, 'detail':'Something went wrong'}
    else:
        return {'res':False,'detail':"Password is invalid. Must contain at least 1 lowercase, 1 uppercase, 1 digit, and 1 special character."}


def send_verification_code(email:str,code:str) -> None:
    sender_email = settings.SENDER_EMAIL
    sender_password = settings.APP_PASSWORD

    subject = 'Verification Code for AILABOT'
    body = f"Your verification code is: {code}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email,sender_password)
            server.sendmail(sender_email,email,msg.as_string())

    except Exception as e:
        raise e
        
      
@transactional
def check_verification_code(session:Session,username:str,user_code:str) -> DefaultRes:
    print(username,user_code)
    user = user_dao.fetchUser(session=session,username=username)
    print(user,username)
    if user is None: return {'res':False,'detail':'User not created'}
    print(user.created_on,datetime.now())
    verif_code = verif_dao.fetchByUserIdLastOne(session,user.id)
    print("CODES",verif_code,user_code)
    print(enc.check_passwords(user_code,verif_code.code),datetime.now(),verif_code.expires_at)
    if enc.check_passwords(user_code,verif_code.code) and datetime.now() < verif_code.expires_at:
        user_dao.updateVerified(session=session,username=username,verified=True)
        return {'res':True,'detail':''}
    else:
        return {'res':False,'detail':'Verification code is not correct'}


@transactional
def send_ver_code(session:Session,user:str|User) -> None:
    print("Rescend Verification Code",user)
    user = user if isinstance(user,User) else user_dao.fetchUser(session,user)
    code = enc.generate_verification_code()
    print(user.user_name,user.email)
    try:
        send_verification_code(user.email,code)
        verification_token = enc.hash_password(code)
        verification_code = Verification_Code(user.id,verification_token,(datetime.now() + timedelta(minutes=int(settings.VERIFICATION_TOKEN_EXPIRE_MINUTES))).isoformat())
        res = verif_dao.create(session,verification_code)
    except Exception as e:
        raise e
    
@transactional
def set_feedback(session:Session,message_id:str,conversation_id:str,feedback:bool=None) ->None:
    message_dao.updateMessageFeedback(session=session,conversation_id=conversation_id,message_id=message_id,feedback=feedback)

@transactional
def create_conversation(session:Session,username:str,conversation_name:str,conv_type:str) -> ConversationType:
    timestamp = datetime.now()
    conv_type = conv_type_dao.fetchConversationTypeByName(session,conv_type)
    user = user_dao.fetchUser(session,username)
    print("USER",user,conv_type.name,conversation_name)
    conversation = Conversation(conversation_name,user.id,timestamp.isoformat(),timestamp.isoformat(),conv_type.id)
    print("CONVERSATION",conversation)
    conversation_dao.createConversation(session,conversation)
    print("NEW CONV",{'conversation_name':conversation_name,'conversation_id':conversation.id,'conversation_type':conv_type.name})
    return {'conversation_name':conversation_name,'conversation_id':conversation.id,'conversation_type':conv_type.name}

@transactional
def update_conversation_by_name(session:Session,username:str,conversation_id:str,conversation_name:str):
    user = user_dao.fetchUser(session,username)
    print(user)
    if user is None: return
    print("WHAT",user.id,conversation_id,conversation_name)
    conversation_dao.updateConversationByNameByUserId(session,user.id,conversation_id,conversation_name)

@transactional
def create_message(session:Session,conversation_id:str,username:str,text:str,role:str, feedback:bool=None) -> MessageType:
    timestamp = datetime.now()
    user = user_dao.fetchUser(session,username)
    if user is None:return
    new_message = Message(conversation_id,user.id,text,timestamp.isoformat(),role,feedback)
    conversation_dao.updateConversationByDate(session,conversation_id,timestamp.isoformat())
    message = message_dao.createMessage(session,new_message)
    return {'id':message.id,'message':message.text,'timestamp':message.date_created_on,'role':message.role,'feedback':message.feedback}

@transactional
def get_token(session:Session,username:str) -> str:
    user = user_dao.fetchUser(session,username)
    if user is None: return 
    session = session_dao.fetchByUserIdLastOne(session,user.id)
    return session.id if session.id else None


@transactional
def create_token(session:Session,username:str,token:str) -> None:
    user = user_dao.fetchUser(session,username)
    if user is None:return 
    timestamp = datetime.now()
    ses_token = SessionModel(user.id,token,timestamp.isoformat())
    session_dao.create(session,ses_token)

@transactional
def get_user_messages(session:Session,username:str,conversation_id:str) -> List[Message]:
    conversation = conversation_dao.fetchConversationByConversationId(session,conversation_id)
    if conversation is not None:
        user_messages = message_dao.fetchMessagesByConversationId(session,conversation_id=conversation_id)
        if user_messages is not None:
            messages = []
            for mes in user_messages:
                messages.append({'id':mes.id,'message':mes.text,'timestamp':str(mes.date_created_on),'role':mes.role, 'feedback':mes.feedback})
            return messages
        else: return []
    else: return []

@transactional
def get_conversations(session:Session,username:str) -> List[ConversationType]:    
    user = user_dao.fetchUser(session,username)
    if user is None: return []
    conversations = conversation_dao.fetchConversationByUserId(session,user.id)
    conv_types = conv_type_dao.fetchConversationType(session)
    conversation_types = {c_type.id:c_type.name for c_type in conv_types}

    return [
        {"conversation_name": conversation.name, "conversation_id": conversation.id, 'conversation_type':conversation_types[conversation.conv_type_id]}
        for conversation in conversations
    ]

@transactional
def create_document_feedback(session:Session,data:DocumentFeedbackDetails):
    print(data)
    user = user_dao.fetchUser(session,data.username)
    print(user)
    if user is None: return
    themes = document_theme_dao.fetchDocumentThemes(session)
    print("THEMES",themes)
    theme_names = [theme.theme for theme in themes]
    print("THEMES NAMES",theme_names)
    if data.theme not in theme_names:
        doc_theme_ = Document_Theme(data.theme,description=None)
        doc_theme = document_theme_dao.createTheme(session,doc_theme_)
    else: doc_theme = document_theme_dao.fetcDocumentThemeByTheme(session,data.theme)
    print("DOC THEME",doc_theme)
    doc_ = Document(doc_theme.id,data.doc_name,data.doc_text,datetime.now().isoformat())
    document = document_dao.createDocument(session,doc_)
    document_feedback = Document_Feedback(data.query_id,data.negative_answer_id,user.id,document.id,data.context)
    document_feedback_dao.createDocument(session,document_feedback)

@transactional
def get_feedback(session:Session):
    feedback = document_feedback_dao.fetchDocsFeedback(session)
    feedbacks = []
    for fd in feedback:
        user = user_dao.fetchUser(session,username=fd.user_id)
        if user is not None: return
        query = message_dao.fetcMessageById(session,fd.query_id).text
        negative_query = message_dao.fetcMessageById(session,fd.negative_query_id).text
        document = document_dao.fetcDocumentById(session,fd.document_id)
        theme = document_theme_dao.fetcDocumentThemeByTheme(session,document.theme_id).theme
        if user:
            feedbacks.append({'username':user.user_name,'user_query':query,'negative_answer':negative_query,'doc_name':document.title,'doc_text':document.content,'context':fd.context,'theme':theme})
    return feedbacks

@transactional
def get_prompt(session:Session,prompt_name:str):
    prompt = prompt_dao.fetchPromptByName(session,prompt_name)
    return prompt.description

@transactional
def get_message_text(session:Session,id:str):
    message = message_dao.fetcMessageById(session,id)
    return message.text

@transactional
def create_document_theme(session:Session,theme:str,description:str|None):
    document_theme = Document_Theme(theme,description)
    document_theme_dao.createTheme(session,document_theme)
    return document_theme

@transactional
def get_document_themes(session:Session):
    themes = document_theme_dao.fetchDocumentThemes(session)
    return [theme.theme for theme in themes]

@transactional
def get_documents_by_theme(session:Session,theme:str):
    theme_id = document_theme_dao.fetcDocumentThemeByTheme(session,theme).id
    documents = document_dao.fetcDocumentByThemeId(session,theme_id)
    return {'documents':[{'title':doc.title,'content':doc.content,'theme':theme} for doc in documents]}

@transactional
def create_document(session:Session,theme:str,doc_name:str,doc_text:str):
    theme_id = document_theme_dao.fetcDocumentThemeByTheme(session,theme).id
    doc = Document(theme_id,doc_name,doc_text,datetime.now().isoformat())
    document = document_dao.createDocument(session,doc)
    return document

@transactional
def get_document_by_name(session:Session,doc_name:str):
    doc = document_dao.fetchByName(session,doc_name)
    return {'title':doc.title,'content':doc.content}
