from fastapi import APIRouter, Response, HTTPException, Cookie
import json
from backend.api.models import UserCredentials, ConversationCreationDetails, NewMessage, Message
from backend.database.core.funcs import login_user, update_token, get_user_messages, get_conversations, create_conversation, create_message
from backend.api.utils import create_access_token, verify_token, initialize_model
from fastapi.responses import StreamingResponse

router = APIRouter()
llm = initialize_model()

@router.post('/login')
async def login(data:UserCredentials, response:Response):
    auth = login_user(username=data.username, password=data.password)
    if auth['authenticated']:
        access_token = create_access_token({'sub':f"{auth['user_details']['username']}+?{auth['user_details']['email']}"})
        print("ACCESS TOKEN: ",access_token)
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

@router.post('/new_conversation')
async def new_conversation(data:ConversationCreationDetails):
    try:
        conversation_name = create_conversation(username=data.username,conversation_name=data.conversation_name)
        return conversation_name
    except Exception as e:
        raise HTTPException(status_code=403, detail=e.detail)
    
@router.post('/new_message')
async def new_message(data:NewMessage):
    print(data)
    try:
        message = create_message(conversation_name=data.conversation_name, text = data.text, role = data.role)
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
async def get_messages(token:str = Cookie(None),conversation_name:str=''):
    print("Access token in GET MESSAGES:", token)
    if not token:
        raise HTTPException(status_code=401, detail='Missing Token')
    try:
        user = verify_token(token)
        if user:
            print("CONVERSATION",conversation_name)
            messages = get_user_messages(conversation_name=conversation_name)
            if len(messages) == 0:
                return []
            return messages
        else:
            raise HTTPException(status_code=401, detail='Invalid or expired token')
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail)      

@router.get('/get_user')
def get_user(token: str = Cookie(None)):
    print("Access token:", token)
    if not token:
        raise HTTPException(status_code=401, detail='Missing Token')
    try:
        user = verify_token(token)
        if user:
            username = user.split('+?')[0]
            email = user.split('+?')[1]
            return {"username":username,"email":email}
        else:
            raise HTTPException(status_code=401, detail='Invalid or expired token')
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail)        

@router.post('/request')
async def chat_endpoint(request: Message):
    print(request)

    #### For LLM open source models via Ollama
    # async def generate():
    #     async for chunk in llm.astream(request.message):
    #         content = chunk.content if hasattr(chunk, 'content') else str(chunk)
    #         print(f"data: {json.dumps({'response': content, 'status': 200})}\n\n")
    #         yield f"data: {json.dumps({'response': content, 'status': 200})}\n\n"
            
    async def generate():
        response = llm.query(request.message)
        if hasattr(response, "response_gen"):
            for chunk in response.response_gen:
                content = str(chunk)
                print(f"data: {json.dumps({'response': content, 'status': 200})}\n\n")
                yield f"data: {json.dumps({'response': content, 'status': 200})}\n\n"
        else:
            # fallback if streaming not supported
            print(f"data: {json.dumps({'response': str(response), 'status': 200})}\n\n")
            yield f"data: {json.dumps({'response': str(response), 'status': 200})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post('/logout')
async def logout(response:Response):
    try:
        response.delete_cookie(key = "token")
        return True
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail) 

