from ..helpers.transactionManagement import transactional
from sqlalchemy.orm import Session
import uuid
from backend.database.daos.user_dao import UserDao
from backend.database.daos.conversation_dao import ConversationDao
from backend.database.daos.user_message_dao import UserMessagesDao
from backend.crypt.encrypt_decrypt import EncryptionDec
from backend.database.entities.messages import UserMessage
from backend.database.entities.conversations import Conversation
from backend.api.models import UserAuthentication
from datetime import datetime,timezone

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
                'user_details':{'username':user.user_name,'email':user.email},
            }
        else:
            return {
                'authenticated':False,
                'detail':'Password is wrong',
                'user_details':{'username':user.user_name,'email':user.email},
            }

@transactional
def create_conversation(session:Session,username:str,conversation_name:str) -> None:
    conversation_dao = ConversationDao()
    user_dao = UserDao()
    timestamp = datetime.now(timezone.utc)
    user = user_dao.fetchUser(session,username)[0]
    conversation = Conversation(
        conversation_id=uuid.uuid4(),
        conversation_name=conversation_name,
        user_id = user.id,
        last_updated=timestamp.isoformat()
    )
    conversation_dao.createConversation(session,conversation)
    return conversation_name

@transactional
def create_message(session:Session,conversation_name:str,text:str,role:str) -> None:
    conversation_dao = ConversationDao()
    user_messages_dao = UserMessagesDao()
    conversation = conversation_dao.fetchConversationByConverastionName(session,conversation_name)[0]
    timestamp = datetime.now(timezone.utc)
    new_message = UserMessage(
        message_id=uuid.uuid4(),
        conversation_id= conversation.id,
        message=text,
        role = role,
        date_created_on=timestamp.isoformat()
    )
    conversation_dao.updateConversationByDate(session,conversation_name=conversation_name,timestamp=timestamp.isoformat())
    message = user_messages_dao.createMessage(session,new_message)
    return {'message':message.message_text,'timestamp':message.date_created_on,'role':message.role}

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
def get_user_messages(session:Session,conversation_name:str) -> list:
    user_messages_dao = UserMessagesDao()
    conversation_dao = ConversationDao()
    conversation = conversation_dao.fetchConversationByConverastionName(session,conversation_name)
    if len(conversation) > 0:
        user_messages = user_messages_dao.fetchMessagesByConversationId(session,conversation_id=conversation[0].id)
        if user_messages:
            messages = []
            for mes in user_messages:
                messages.append({'message':mes.message_text,'timestamp':str(mes.date_created_on),'role':mes.role})
            print("GEt User Messages",messages)
            return messages
        else: return []
    else: return []

@transactional
def get_conversations(session:Session,username:str) -> list:
    conversation_dao = ConversationDao()
    user_dao = UserDao()
    user = user_dao.fetchUser(session,username)[0].id
    conversations = conversation_dao.fetchConversationByUserId(session,user)
    return [conversation.conversation_name for conversation in conversations]