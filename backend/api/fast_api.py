"""
FastAPI Router: Authentication, User Management, Conversations, and Chat API

This module defines the HTTP API endpoints exposed by the backend. It handles:
- User login, registration, verification, and logout
- Conversation creation, update, retrieval
- Messaging (new messages, fetch messages)
- Feedback on messages
- Integration with the LLM pipeline for legal Q&A

Each endpoint validates input via Pydantic models and returns structured responses.
"""

from fastapi import APIRouter, Response, HTTPException, Cookie, Request
import json
from backend.api.models import (
    UserFeedback,
    UserOpenData,
    VerifCode,
    UserCredentials,
    ConversationCreationDetails,
    UserData,
    NewMessage,
    Message,
    UpdateConversationDetails,
)
from backend.database.core.funcs import (
    update_conv,
    set_feedback,
    resend_ver_code,
    check_verification_code,
    check_create_user_instance,
    login_user,
    update_token,
    get_user_messages,
    get_conversations,
    create_conversation,
    create_message,
)
from backend.api.utils import create_access_token, verify_token
from fastapi.responses import StreamingResponse, JSONResponse
from langchain_openai import ChatOpenAI
from backend.database.config.config import settings

router = APIRouter()


@router.post("/login")
async def login(data: UserCredentials, response: Response):
    """
    Authenticate a user and set JWT as cookie.

    Request Body
    ------------
    UserCredentials {username: str, password: str}

    Returns
    -------
    dict
        {'user_details': {...}} if successful.

    Raises
    ------
    HTTPException 401
        If authentication fails.
    """
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



@router.post("/register")
async def register(data: UserData):
    """
    Register a new user account.

    Request Body
    ------------
    UserData {username: str, password: str, email: str}

    Returns
    -------
    bool
        True if registration successful.

    Raises
    ------
    HTTPException 401
        If username or email already exists, or invalid password.
    """
    res = check_create_user_instance(username = data.username, password= data.password, email= data.email)
    if res['res']:
        return True
    else:
        raise HTTPException(status_code=401,detail=res['detail'])  
 

@router.post("/verify")
async def verify(data: VerifCode):
    """
    Verify a user's email using a code.

    Request Body
    ------------
    VerifCode {username: str, code: str}

    Returns
    -------
    bool
        True if verification successful.

    Raises
    ------
    HTTPException 401
        If code expired or mismatched.
    """
    res = check_verification_code(username=data.username,user_code=data.code)
    if res['res']:
        return True
    else:
        raise HTTPException(status_code=401,detail=res['detail']) 

@router.post("/resend-code")
async def resend_code(data: UserOpenData):
    """
    Resend a verification code to a user's email.

    Request Body
    ------------
    UserOpenData {username: str, email: str}

    Returns
    -------
    bool
        True if code resent.
    """
    try:
        resend_ver_code(username=data.username,email=data.email)
        return True 
    except Exception as e:
        raise e
    

@router.post("/new_conversation")
async def new_conversation(data: ConversationCreationDetails):
    """
    Create a new conversation.

    Request Body
    ------------
    ConversationCreationDetails {username: str, conversation_name: str}

    Returns
    -------
    dict
        {'conversation_name': str, 'conversation_id': UUID}
    """
    try:
        conversation = create_conversation(username=data.username,conversation_name=data.conversation_name)
        return conversation
    except Exception as e:
        raise HTTPException(status_code=403, detail=e.detail)
    
@router.post("/update_conversation")
async def update_conversation(data: UpdateConversationDetails):
    """
    Update the name of an existing conversation.

    Request Body
    ------------
    UpdateConversationDetails {conversation_id: str, conversation_name: str}

    Returns
    -------
    bool
        True if update successful.
    """
    try:
        update_conv(conversation_name=data.conversation_name,conversation_id=data.conversation_id)
        return True
    except Exception as e:
        raise HTTPException(status_code=403, detail=e.detail)

@router.post("/new_message")
async def new_message(data: NewMessage):
    """
    Create a new message in a conversation.

    Request Body
    ------------
    NewMessage {id: str, conversation_id: str, text: str, role: str, feedback: bool|None}

    Returns
    -------
    dict
        {'id': str, 'message': str, 'timestamp': str, 'role': str}
    """
    try:
        message = create_message(conversation_id=data.conversation_id, text = data.text, role = data.role, id=data.id, feedback=data.feedback)
        return message
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail)  
    
@router.get("/user_conversations")
async def get_user_conversations(token: str = Cookie(None), username: str = ""):
    """
    Fetch all conversations for a given user.

    Query Parameters
    ----------------
    username : str
        The username whose conversations to fetch.

    Returns
    -------
    list[dict]
        [{'conversation_name': str, 'conversation_id': UUID}, ...]
    """
    try:
        conversations = get_conversations(username=username)
        return conversations
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail)  
    

@router.get("/messages")
async def get_messages(token: str = Cookie(None), conversation_id: str = ""):
    """
    Fetch messages for a given conversation.

    Query Parameters
    ----------------
    conversation_id : str
        ID of the conversation.

    Returns
    -------
    list[dict]
        List of messages in ascending timestamp order.
    """
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

@router.post("/user_feedback")
def user_feedback(data: UserFeedback):
    """
    Submit feedback for a user message.

    Request Body
    ------------
    UserFeedback {message_id: str, conversation_id: str, feedback: bool|None}
    """
    try:
        set_feedback(message_id=data.message_id,conversation_id=data.conversation_id,feedback=data.feedback)
    except Exception as e:
        raise e

@router.get("/get_user")
def get_user(token: str = Cookie(None)):
    """
    Retrieve user details from JWT token.

    Returns
    -------
    dict
        {'username': str, 'email': str, 'verified': bool|None}
    """
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

@router.post("/request")
async def chat_endpoint(request_data: Message, request: Request):
    """
    Main chat endpoint integrating with the LLM pipeline.

    Request Body
    ------------
    Message {message: str, conversation_history: list[dict]}

    Returns
    -------
    StreamingResponse
        Streamed LLM-generated response (Server-Sent Events).
    JSONResponse
        If the query is rejected as unsafe or non-legal.
    """

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
    pipeline = request.app.state.pipeline 
    llm_params = pipeline.run_full_pipeline(request_data.message)
    
    if isinstance(llm_params, dict):
        model = ChatOpenAI(model=settings.OPEN_AI_MODEL,api_key=settings.API_KEY, temperature=0.7)
        llm_params['conversation_history'] = request_data.conversation_history if len(request_data.conversation_history)!=0 else []
        async def generate():
            try:
                async for chunk in model.astream(prompt.format(**llm_params)):
                    content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                    yield f"data: {json.dumps({'response': content, 'status': 200})}\n\n"

            except Exception as e:
                # Log error details            
                # OR raise it, if you don't want partial yield
                raise HTTPException(status_code=500, detail="Internal Server Error during LLM generation.")
            
            return StreamingResponse(generate(), media_type="text/event-stream")
    else: return JSONResponse(content={"response": llm_params, "status": 200})
        
@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by clearing JWT cookie.

    Returns
    -------
    bool
        True if logout successful.
    """
    try:
        response.delete_cookie(key = "token")
        return True
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail) 

