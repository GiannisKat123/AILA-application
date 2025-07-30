from ..helpers.transactionManagement import transactional
from sqlalchemy.orm import Session
import uuid
from backend.database.daos.user_dao import UserDao
from backend.database.daos.conversation_dao import ConversationDao
from backend.database.daos.user_message_dao import UserMessagesDao
from backend.crypt.encrypt_decrypt import EncryptionDec
from backend.database.entities.messages import UserMessage
from backend.database.entities.conversations import Conversation
from backend.database.entities.user import User
from backend.api.models import UserAuthentication
from datetime import datetime,timezone,timedelta
from backend.database.config.config import settings
import smtplib
from email.mime.text import MIMEText

@transactional
def login_user(session:Session,username:str,password:str) -> UserAuthentication:
    user_dao = UserDao()
    enc = EncryptionDec()
    users_fetched = user_dao.fetchUser(session,username)
    if len(users_fetched) == 0:
        return {
            'authenticated':False,
            'detail':'No user was found with that username',
            'user_details':None
        }
    for user in users_fetched:
        if enc.check_passwords(password,user.password):
            return {
                'authenticated':True,
                'detail':'',
                'user_details':{'username':user.user_name,'email':user.email, 'verified': user.verified},
            }
        else:
            return {
                'authenticated':False,
                'detail':'Password is wrong',
                'user_details':{'username':user.user_name,'email':user.email},
            }

@transactional
def check_create_user_instance(session:Session, username:str, password:str, email:str):
    user_dao = UserDao()
    enc = EncryptionDec()
    user_in_database = user_dao.fetchUser(session=session,username=username)
    user_email_in_database = user_dao.fetchUserByEmail(session=session,email=email)
    if len(user_in_database) > 0:
        return {'res':False,'detail':'User already exists'}
    elif len(user_email_in_database) > 0:
        return {'res':False,'detail':'Email already exists'}
    elif enc.is_valid_password(password):
        code = enc.generate_verification_code()
        user = User(
            session_id = str(uuid.uuid4()),
            user_name= username,
            password= password,
            email=email,
            role = 'user',
            verification_code= code,
            date_created_on=datetime.now(timezone.utc).isoformat()
        )
        res = user_dao.createUser(session=session,user_data=user)
        if res: 
            send_verification_code(email=email,code = code)
            return {'res':True, 'detail':code}
        else: return {'res':False, 'detail':'Something went wrong'}
    else:
        return {'res':False,'detail':"Password is invalid. Must contain at least 1 lowercase, 1 uppercase, 1 digit, and 1 special character."}


def send_verification_code(email:str,code:str):
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
def check_verification_code(session:Session,username:str,user_code:str):
    user_dao = UserDao()
    user = user_dao.fetchUser(session=session,username=username)[0]
    if datetime.now(timezone.utc) > user.code_created_on + timedelta(minutes=2):
        return {'res':False,'detail':'Verification code expired'}
    elif user_code != user.verification_code:
        return {'res':False,'detail':'Verification code does not match'}
    else:
        user_dao.updateVerified(session=session,username=username)
        return {'res':True,'detail':''}

@transactional
def resend_ver_code(session:Session,username:str,email:str):
    user_dao = UserDao()
    enc = EncryptionDec()
    code = enc.generate_verification_code()
    try:
        user_dao.updateVerCode(session=session,username=username,code=code,code_created_on=datetime.now(timezone.utc).isoformat())
        send_verification_code(email=email,code = code)
    except Exception as e:
        raise e
    

@transactional
def set_feedback(session:Session,message_id:str,conversation_id:str,feedback:bool=None):
    message_dao = UserMessagesDao()
    message_dao.updateMessageFeedback(session=session,conversation_id=conversation_id,message_id=message_id,feedback=feedback)

@transactional
def create_conversation(session:Session,username:str,conversation_name:str) -> None:
    conversation_dao = ConversationDao()
    user_dao = UserDao()
    timestamp = datetime.now(timezone.utc)
    user = user_dao.fetchUser(session,username)[0]
    conversation_id = uuid.uuid4()
    conversation = Conversation(
        conversation_id=conversation_id,
        conversation_name=conversation_name,
        user_id = user.id,
        last_updated=timestamp.isoformat()
    )
    conversation_dao.createConversation(session,conversation)
    return {'conversation_name':conversation_name,'conversation_id':conversation_id}

@transactional
def update_conv(session:Session,conversation_id:str,conversation_name:str):
    conversation_dao = ConversationDao()
    conversation_dao.updateConversationByName(session,conversation_id,conversation_name)
    return

@transactional
def create_message(session:Session,conversation_id:str,text:str,role:str, id:str, feedback:bool=None) -> None:
    conversation_dao = ConversationDao()
    user_messages_dao = UserMessagesDao()
    timestamp = datetime.now(timezone.utc)
    new_message = UserMessage(
        message_id=id,
        conversation_id= conversation_id,
        message=text,
        role = role,
        feedback=feedback,
        date_created_on=timestamp.isoformat()
    )
    conversation_dao.updateConversationByDate(session,conversation_id=conversation_id,timestamp=timestamp.isoformat())
    message = user_messages_dao.createMessage(session,new_message)
    return {'id':message.id,'message':message.message_text,'timestamp':message.date_created_on,'role':message.role}

@transactional
def update_token(session:Session,username:str,token:str) -> None:
    user_dao = UserDao()
    user = user_dao.fetchUser(session,username)[0]
    user_dao.updateToken(session,user.id,token)

@transactional
def get_token(session:Session,username:str) -> str:
    user_dao = UserDao()
    user = user_dao.fetchUser(session,username)[0]
    return user.session_id if user.session_id else None

@transactional
def get_user_messages(session:Session,conversation_id:str) -> list:
    user_messages_dao = UserMessagesDao()
    user_messages = user_messages_dao.fetchMessagesByConversationId(session,conversation_id=conversation_id)
    if user_messages:
        messages = []
        for mes in user_messages:
            messages.append({'id':mes.id,'message':mes.message_text,'timestamp':str(mes.date_created_on),'role':mes.role, 'feedback':mes.feedback})
        return messages
    else: return []

@transactional
def get_conversations(session:Session,username:str) -> list:
    conversation_dao = ConversationDao()
    user_dao = UserDao()
    user = user_dao.fetchUser(session,username)[0].id
    conversations = conversation_dao.fetchConversationByUserId(session,user)
    return [{'conversation_name':conversation.conversation_name,'conversation_id':conversation.id} for conversation in conversations]