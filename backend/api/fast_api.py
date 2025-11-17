from fastapi import APIRouter, Response, HTTPException, Cookie, UploadFile, File, Form, Depends, Request
import os, json
from backend.api.models import (
    DocumentFeedbackDetails,
    VerifyUser,
    UserCredentials,
    ConversationCreationDetails, 
    UserData ,
    UpdateConversation,
    Message,
    UserMessage,
    UserDataReg,
    ConversationType
)
from backend.database.core.funcs import (
    login_user,
    create_token,
    create_user_instance,
    check_verification_code,
    send_ver_code,
    create_document_feedback,
    create_conversation,
    update_conversation_by_name,
    create_message,
    get_conversations,
    get_user_messages,
    set_feedback,
    get_prompt
)
from backend.api.utils import create_access_token, verify_token
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from backend.database.config.config import settings
from typing import Optional,List
from backend.api.utils import parse_message_form
from backend.api.prompt_utilities import persist_upload, build_messages, create_word_file
from backend.api.aws_funcs import get_client, upload, download

router = APIRouter()

@router.post('/login')
async def login(data:UserCredentials, response:Response):
    auth = login_user(username=data.username, password=data.password)
    if auth['authenticated']:
        print(auth)
        access_token = create_access_token({'sub':f"{auth['user_details']['username']}+?{auth['user_details']['email']}+?{auth['user_details']['verified']}+?{auth['user_details']['role']}"})
        create_token(username = data.username,token=access_token)
        response.set_cookie(
            key = "token",
            value=access_token,
            httponly=True,
            secure = False, # True in production  
            samesite = "lax"
        )
        return {'user_details':auth['user_details']}
    else:
        raise HTTPException(status_code=401,detail=auth['detail'])     


@router.post('/register')
async def register(data:UserDataReg,response:Response):
    res = create_user_instance(username = data.username, password= data.password, email= data.email, role=data.role)
    if res['res']:
        access_token = create_access_token({'sub':f"{data.username}+?{data.email}+?False+?{data.role}"})
        create_token(username = data.username,token=access_token)
        response.set_cookie(
            key = "token",
            value=access_token,
            httponly=True,
            secure = False, # True in production  
            samesite = "lax"
        )
        return True
    else:
        raise HTTPException(status_code=401,detail=res['detail'])  
 

@router.post('/verify')
async def verify(data:VerifyUser,response:Response):
    print(data)
    res = check_verification_code(username=data.username,user_code=data.verification_code)
    print('Verification',res)
    if res['res']:
        response.delete_cookie(key = "token")
        return True
    else:
        raise HTTPException(status_code=401,detail=res['detail']) 

@router.post('/send_code')
async def send_code(data:UserData):
    try:
        send_ver_code(user=data.username)
        return True 
    except Exception as e:
        raise e
    
@router.post('/new_document_feedback')
async def document_feedback(data:DocumentFeedbackDetails):
    try:
        create_document_feedback(data=data)
        return True
    except Exception as e:
        raise HTTPException(status_code=403,detail=str(e))
        
@router.post('/new_conversation')
async def new_conversation(data:ConversationCreationDetails):
    try:
        conversation = create_conversation(username=data.username,conversation_name=data.conversation_name,conv_type=data.conversation_type)
        if conversation is not None:
            print('new_conversation',conversation)
        else:print("WHAT THE FUCK")
        return conversation
        # return create_conversation(username=data.username,conversation_name=data.conversation_name,conv_type=data.conversation_type)
    except Exception as e:
        print("WHAAAAAAATTTTT",repr(e))
        raise HTTPException(status_code=403, detail=str(e))
    
@router.post('/update_conversation')
async def update_conversation_name(data:UpdateConversation):
    try:
        print(data)
        update_conversation_by_name(username=data.username,conversation_id=data.conversation_id,conversation_name=data.conversation_name)
        return True
    except Exception as e:
        print(e)
        print(e.detail)
        raise HTTPException(status_code=403, detail=str(e))    

@router.post('/new_message')
async def new_message(data:Message):
    print(data)
    try:
        message = create_message(conversation_id=data.conversation_id,username=data.username,text=data.text,role=data.role,feedback=data.feedback)
        return message
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail)  

@router.get('/conversations')
async def get_user_conversations(token:str=Cookie(None),username:str=''):
    if not token: raise HTTPException(status_code=401,detail='Missing Token')
    try:
        conversations = get_conversations(username=username)
        return conversations
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail)
    
@router.get('/messages')
async def get_messages(token:str=Cookie(None),username:str='',conversation_id:str=''):
    if not token: raise HTTPException(status_code=401,detail='Missing Token')
    try:
        user = verify_token(token)
        if user is not None:
            messages = get_user_messages(username=username,conversation_id=conversation_id)
            if len(messages) == 0 : return []
            else: return messages
        else:  raise HTTPException(status_code=401, detail='Invalid or expired token')
    except Exception as e: 
        raise HTTPException(status_code=403, detail=e) 


@router.post('/user_feedback')
def user_feedback(data:Message):
    try:
        set_feedback(message_id=data.message_id,conversation_id=data.conversation_id,feedback=data.feedback)
        return True
    except Exception as e:
        raise e

@router.get('/get_user')
def get_user(token: str = Cookie(None)):
    print("Access token:", token)
    if token is None: raise HTTPException(status_code=401, detail='Missing Token')
    try:
        user = verify_token(token)
        if user:
            print(user.split('+?'))
            username = user.split('+?')[0]
            email = user.split('+?')[1]
            verified = user.split('+?')[2]
            role = user.split('+?')[3]
            if 'true' in str(verified).lower():
                verified = True
            elif 'false' in str(verified).lower():
                verified = False
            else:
                verified = None
            return {"username":username,"email":email,'verified':verified,'role':role}
        else:
            raise HTTPException(status_code=401, detail='Invalid or expired token')
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail)        


@router.post('/logout')
async def logout(response:Response):
    try:
        response.delete_cookie(key = "token")
        return True
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail) 
    
@router.post('/get_ai_conversation_title')
async def create_ai_conversation_title(data:Message):
    model = ChatOpenAI(model=settings.OPEN_AI_MODEL,api_key=settings.OPENAI_API_KEY, temperature=0.7)
    prompt = get_prompt(prompt_name = 'ai_conversation_title_creation')
    try:
        response = model.invoke(prompt.format(first_query = data.text))
        return response
    except Exception as e:
        raise HTTPException(status_code=403,detail=str(e))

@router.post('/request')
async def chat_endpoint(data:UserMessage = Depends(parse_message_form),files:Optional[List[UploadFile]] = File(None),request:Request=None):
    model = ChatOpenAI(model=settings.OPEN_AI_MODEL,api_key=settings.OPENAI_API_KEY, temperature=0.7)
    if data['conversation_type'] == 'lawsuit':
        path = 'backend/api/docs_for_lawsuits'
        docs = os.listdir(path)
        texts = []
        for doc in docs:
            with open(path + f'/{doc}',encoding = 'utf-8') as f:
                text = f.read()
            texts.append(text)
        
        if data['conversation_id'] not in request.app.state.user_data_dict.keys(): request.app.state.user_data_dict[data['conversation_id']] = {}
        language_prompt = get_prompt(prompt_name='language_detection')
        response = model.invoke(language_prompt.format(message=data['message']))
        language = str(response.content).strip()
        
        files_list = [persist_upload(file) for file in files] if files else []

        file_description_prompt = get_prompt(prompt_name='file_description')
        messages = build_messages(file_description_prompt,files_list)
        files_description = model.invoke(messages)

        lawsuit_prompt1 = get_prompt(prompt_name='lawsuit_prompt_1').format(documents = texts, conversation_history = data['conversation_history'], query = data['message'], language = language, state=request.app.state.user_data_dict[data['conversation_id']], evidence_lines = files_description.content)
        lawsuit_few_shot_prompt1 = get_prompt(prompt_name='lawsuit_few_shot_prompt_1')

        prompt_full = lawsuit_prompt1 + "\n\n" + lawsuit_few_shot_prompt1

        messages = build_messages(prompt_full,files_list)
        json_model = model.bind(response_format = {'type':'json_object'})
        response = json_model.invoke(messages)
        resp_dict = json.loads(response.content)

        if request.app.state.user_data_dict[data['conversation_id']] == {}: request.app.state.user_data_dict[data['conversation_id']] = resp_dict
        else:
            for key in resp_dict.keys():
                if key != 'parsed_data': request.app.state.user_data_dict[data['conversation_id']][key] = resp_dict[key]
            for key in resp_dict['parsed_data']: request.app.state.user_data_dict[data['conversation_id']]['parsed_data'][key] = resp_dict['parsed_data'][key]

        if request.app.state.user_data_dict[data['conversation_id']]['status'] == 'READY':
            lawsuit_prompt2 = get_prompt(prompt_name='lawsuit_prompt_2').format(parsed_data = request.app.state.user_data_dict[data['conversation_id']]['parsed_data'],
                        documents = texts,
                            conversation_history = data['conversation_history'],
                            query = text,
                                language = 'greek',
                                to = str(request.app.state.user_data_dict[data['conversation_id']]['parsed_data']['prosecutor_place']),
                                procecutor = str(request.app.state.user_data_dict[data['conversation_id']]['parsed_data']['complainant']),
                                accused = str(request.app.state.user_data_dict[data['conversation_id']]['parsed_data']['complainant']),
                                place_date = str(request.app.state.user_data_dict[data['conversation_id']]['parsed_data']['prosecutor_place'])
                                )
            response = model.invoke(lawsuit_prompt2)
            response_content = str(response.content).strip()
            file_lists = [persist_upload(file) for file in files] if files else []
            out_path, filename = create_word_file(response_content, files_list)
            s3_client = get_client()
            upload(out_path + f'//{filename}',filename,s3_client)
            url = download(filename,s3_client)
            s3_client.close()
            response_content += f'\n Below you can download a word file of the document too from the following URL: {url}'

            async def fake_stream(): yield f"data: {json.dumps({'response':response_content,'status':200})}\n\n"

            return StreamingResponse(fake_stream(),media_type='text/event-stream')
        
        else:
            async def fake_stream(): yield f"data: {json.dumps({'response': request.app.state.user_data_dict[data['conversation_id']]['questions_el'], 'status': 200})}\n\n"

            return StreamingResponse(fake_stream(), media_type="text/event-stream")

    if data['conversation_type'] == 'normal':
        prompt = get_prompt(prompt_name='normal_prompt')
        pipeline = request.app.state.pipeline 
        app_workflow = request.app.state.app
        llm_params = pipeline.run_full_pipeline(data['message'],data['conversation_history'],app_workflow,web_search_activation=data['web_search_tool'])        

        if isinstance(llm_params, dict):
            
            prompt = prompt.format(**llm_params)

            async def generate():
                try:
                    async for chunk in model.astream(prompt):
                        content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                        yield f"data: {json.dumps({'response': content, 'status': 200})}\n\n"

                except Exception as e:
                    raise HTTPException(status_code=500, detail="Internal Server Error during LLM generation.")
                
            return StreamingResponse(generate(), media_type="text/event-stream")
        elif isinstance(llm_params, str):
            async def fake_stream():
                yield f"data: {json.dumps({'response': llm_params, 'status': 200})}\n\n"

            return StreamingResponse(fake_stream(), media_type="text/event-stream")
        else:
            raise HTTPException(status_code=500, detail="Unexpected pipeline output.")

@router.post('/automated_message')
async def automated_ai_response(data:ConversationType):
    try:
        ai_message = get_prompt(prompt_name=f'{data.conversation_type}_automated_message')
        return ai_message
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=str(e))