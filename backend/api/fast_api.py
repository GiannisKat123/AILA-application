from fastapi import APIRouter, Response, HTTPException, Cookie, Request
import json
from backend.api.models import UserFeedback,UserOpenData,VerifCode,UserCredentials, ConversationCreationDetails, UserData ,NewMessage, Message, UpdateConversationDetails
from backend.database.core.funcs import update_conv,set_feedback,resend_ver_code,check_verification_code, check_create_user_instance ,login_user, update_token, get_user_messages, get_conversations, create_conversation, create_message
from backend.api.utils import create_access_token, verify_token
from fastapi.responses import StreamingResponse
from langchain.prompts import PromptTemplate 
from langchain_openai import ChatOpenAI
from backend.database.config.config import settings

router = APIRouter()

@router.post('/login')
async def login(data:UserCredentials, response:Response):
    auth = login_user(username=data.username, password=data.password)
    if auth['authenticated']:
        access_token = create_access_token({'sub':f"{auth['user_details']['username']}+?{auth['user_details']['email']}+?{auth['user_details']['verified']}"})
        update_token(username=auth['user_details']['username'], token=access_token)
        response.set_cookie(
            key = "token",
            value=access_token,
            httponly=True,
            secure = True, # True in production  
            samesite = "none"
        )
        return {'user_details':auth['user_details']}
    else:
        raise HTTPException(status_code=401,detail=auth['detail'])     


@router.post('/register')
async def register(data:UserData):
    res = check_create_user_instance(username = data.username, password= data.password, email= data.email)
    if res['res']:
        return True
    else:
        raise HTTPException(status_code=401,detail=res['detail'])  
 

@router.post('/verify')
async def verify(data:VerifCode):
    res = check_verification_code(username=data.username,user_code=data.code)
    if res['res']:
        return True
    else:
        raise HTTPException(status_code=401,detail=res['detail']) 

@router.post('/resend-code')
async def resend_code(data:UserOpenData):
    try:
        resend_ver_code(username=data.username,email=data.email)
        return True 
    except Exception as e:
        raise e
    

@router.post('/new_conversation')
async def new_conversation(data:ConversationCreationDetails):
    try:
        conversation = create_conversation(username=data.username,conversation_name=data.conversation_name)
        return conversation
    except Exception as e:
        raise HTTPException(status_code=403, detail=e.detail)
    
@router.post('/update_conversation')
async def update_conversation(data:UpdateConversationDetails):
    try:
        update_conv(conversation_name=data.conversation_name,conversation_id=data.conversation_id)
        return True
    except Exception as e:
        raise HTTPException(status_code=403, detail=e.detail)

@router.post('/new_message')
async def new_message(data:NewMessage):
    try:
        message = create_message(conversation_id=data.conversation_id, text = data.text, role = data.role, id=data.id, feedback=data.feedback)
        return message
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail)  
    
@router.get('/user_conversations')
async def get_user_conversations(token:str = Cookie(None),username:str=''):
    try:
        conversations = get_conversations(username=username)
        return conversations
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail)  
    

@router.get('/messages')
async def get_messages(token:str = Cookie(None),conversation_id:str=''):
    if not token:
        raise HTTPException(status_code=401, detail='Missing Token')
    try:
        user = verify_token(token)
        if user:
            messages = get_user_messages(conversation_id=conversation_id)
            if len(messages) == 0:
                return []
            return messages
        else:
            raise HTTPException(status_code=401, detail='Invalid or expired token')
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail)      

@router.post('/user_feedback')
def user_feedback(data:UserFeedback):
    try:
        set_feedback(message_id=data.message_id,conversation_id=data.conversation_id,feedback=data.feedback)
    except Exception as e:
        raise e

@router.get('/get_user')
def get_user(token: str = Cookie(None)):
    if not token:
        raise HTTPException(status_code=401, detail='Missing Token')
    try:
        user = verify_token(token)
        if user:
            username = user.split('+?')[0]
            email = user.split('+?')[1]
            verified = user.split('+?')[2]
            if 'true' in str(verified).lower():
                verified = True
            elif 'false' in str(verified).lower():
                verified = False
            else:
                verified = None
            return {"username":username,"email":email,'verified':verified}
        else:
            raise HTTPException(status_code=401, detail='Invalid or expired token')
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail)        

@router.post('/request')
async def chat_endpoint(request_data: Message,request:Request):

    prompt = """
        You are a highly competent legal assistant designed to provide accurate, well-reasoned, and context-aware answers to legal questions. Your responses should be clear, concise, and grounded in the provided legal context and conversation history.

        Your task is to analyze the question posed by the user and generate a helpful answer based on the information available. If necessary, synthesize knowledge from both legal documents and prior conversation to ensure completeness and legal soundness.

        You have access to the following sources of information:

        1. **Conversation History**: This includes prior interactions with the user, which may contain clarification, additional details, or follow-up questions. Use this to maintain coherence and continuity.
            {conversation_history}

        2. **Legal Context**: This includes relevant legal texts, regulations, court decisions, or authoritative commentary provided as context. Use this as your primary source of legal truth.
            
            RAG CONTEXT: {summarized_context}

            SEARCH RESULTS: {search_results}

        3. **User's Current Question**: This is the specific legal inquiry that you must address:
            {query}

        Instructions:
        - Prioritize factual correctness and legal validity.
        - If the context contains conflicting information, acknowledge the ambiguity and respond cautiously.
        - Do not fabricate laws, articles, or cases.
        - If the question cannot be answered based on the context, state that clearly and suggest next steps if possible.
        - Structure your answer logically, and cite the context or conversation elements when appropriate.
        - Keep the most relevant information that can help you answer the user query. Keep also related metadata in your response.

        If you have metadata related to the context, include it in your response as well.

        Generate your answer below in {language}:
    """

    prompt = PromptTemplate(input_variables=['query','summarized_context','conversation_history','search_results','language'],template=prompt)
    model = ChatOpenAI(model=settings.OPEN_AI_MODEL,api_key=settings.API_KEY,temperature=0.7,streaming=True)
    agent_chain = prompt | model

    pipeline = request.app.state.pipeline
    app = request.app.state.app
    
    llm_params = pipeline.get_context_from_graph(app,request_data.message)

    llm_params['conversation_history'] = request_data.conversation_history if len(request_data.conversation_history)!=0 else []

    async def generate():
        try:
            async for chunk in agent_chain.astream(llm_params):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                yield f"data: {json.dumps({'response': content, 'status': 200})}\n\n"

        except Exception as e:
            # Log error details            
            # OR raise it, if you don't want partial yield
            raise HTTPException(status_code=500, detail="Internal Server Error during LLM generation.")
        
    return StreamingResponse(generate(), media_type="text/event-stream")

@router.post('/logout')
async def logout(response:Response):
    try:
        response.delete_cookie(key = "token")
        return True
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail) 

