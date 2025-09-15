from fastapi import APIRouter, Response, HTTPException, Cookie, Request, UploadFile, File, Form, Depends
import json
from backend.api.models import DocumentFeedbackDetails,UserFeedback,UserOpenData,VerifCode,UserCredentials, ConversationCreationDetails, UserData ,NewMessage, Message, UpdateConversationDetails
from backend.database.core.funcs import create_document_feedback,update_conv,set_feedback,resend_ver_code,check_verification_code, check_create_user_instance ,login_user, update_token, get_user_messages, get_conversations, create_conversation, create_message
from backend.api.utils import create_access_token, verify_token
from fastapi.responses import StreamingResponse,JSONResponse
from langchain.prompts import PromptTemplate 
from langchain_openai import ChatOpenAI
from backend.database.config.config import settings
import os, json
from typing import Optional, List
from backend.api.prompt_utilities import persist_upload, build_messages

router = APIRouter()

@router.post('/login')
async def login(data:UserCredentials, response:Response):
    auth = login_user(username=data.username, password=data.password)
    print(auth)
    if auth['authenticated']:
        access_token = create_access_token({'sub':f"{auth['user_details']['username']}+?{auth['user_details']['email']}+?{auth['user_details']['verified']}+?{auth['user_details']['role']}"})
        update_token(username=auth['user_details']['username'], token=access_token)
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
async def register(data:UserData):
    res = check_create_user_instance(username = data.username, password= data.password, email= data.email,role = data.role)
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
    
@router.post('/new_document_feedback')
async def new_document_feed(data:DocumentFeedbackDetails):
    try:
        create_document_feedback(data=data)
        return True
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail=e.detail)
    

@router.post('/new_conversation')
async def new_conversation(data:ConversationCreationDetails):
    try:
        conversation = create_conversation(username=data.username,conversation_name=data.conversation_name, conversation_type = data.conversation_type)
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
        print(conversations)
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
    print(data)
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
            print(user,user.split('+?'))
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

async def parse_message_form(
    message: Optional[str] = Form(None),
    conversation_type: Optional[str] = Form(None),
    web_search_tool: Optional[str] = Form(None),
    conversation_history: Optional[str] = Form(None),
) -> dict:
    # Validate presence
    missing = [k for k,v in {
        "message": message,
        "conversation_type": conversation_type,
    }.items() if v in (None, "")]
    if missing:
        raise HTTPException(status_code=400, detail={"error":"missing_fields","fields":missing})

    # Coerce boolean
    web_search = str(web_search_tool).strip().lower() in {"1","true","yes","on"} if web_search_tool is not None else False

    # Coerce history JSON (must be list)
    hist_raw = conversation_history if conversation_history not in (None, "", "null") else "[]"
    try:
        history = json.loads(hist_raw)
        if not isinstance(history, list):
            raise ValueError("conversation_history must be a JSON array")
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error":"bad_conversation_history","reason":str(e)})

    return {
        "message": message,
        "conversation_type": conversation_type,
        "web_search_tool": web_search,
        "conversation_history": history,
    }


@router.post('/request')
async def chat_endpoint(request_data: Message = Depends(parse_message_form),files: Optional[List[UploadFile]] = File(None),request:Request=None):

    print(request_data.keys())
    model = ChatOpenAI(model=settings.OPEN_AI_MODEL,api_key=settings.API_KEY, temperature=0.7,)

    if request_data['conversation_type'] == 'lawsuit':
        path = 'backend/api/docs_for_lawsuits'
        docs = os.listdir(path)
        texts = []
        for doc in docs:
            with open(path+f'/{doc}',encoding='utf-8') as file:
                text = file.read()
            texts.append(text)


        prompt = """Find the language used in the following query: {message}"""
        
        # Match the placeholder name with the keyword argument
        response = model.invoke(prompt.format(message=request_data['message']))
        
        response_content = str(response.content).strip()
        language = response_content

        file_list = [persist_upload(file) for file in files] if files else []
        

        prompt = """You are a meticulous legal drafting assistant for Greek criminal complaints about phishing/cyber fraud.
            Produce a complete, formally styled criminal complaint (Μήνυση) that mirrors authentic filings before Greek Prosecutors.
            Write the complaint **in Greek**, using clear sections, precision, numbering, and strictly chronological narration where relevant.

            === DATA NEEDED ===
            1. Complainant’s details: Full name, Address, Phone number, Email.
            2. Accused’s details (if known): Full name/Company, Contact information, IBAN, etc.
            3. Detailed description of events: How the phishing occurred, through which platform, amounts involved.
            4. Chronological timeline: Dates/times and events in order.
            5. Transactions: Exact dates, amounts, payment method, IBAN, references.
            6. Evidence available: Screenshots, receipts, messages, URLs, emails, phone numbers.
            7. Place & Prosecutor: The city where the complaint is filed (e.g., “TO: The Prosecutor of First Instance of Athens”)
                and the place of commission/reference (e.g., Athens, 01/09/2025).

            === DRAFTING RULES ===
            1) Use ONLY the provided data. If a field is missing, insert a clear placeholder like "[…]".
            2) Dates must follow DD/MM/YYYY. Monetary amounts in Euro with thousand separators and two decimals, e.g., 1.234,56 €.
            3) Enumerate transactions, phone numbers, emails, URLs, and pieces of evidence.
            4) Legal basis (succinct): Article 386 ΠΚ (fraud) and/or Article 386A ΠΚ (computer fraud). Mention “κατ’ εξακολούθηση” where applicable.
            5) Include an explicit request for investigation by the Cyber Crime Division (Διεύθυνση Δίωξης Ηλεκτρονικού Εγκλήματος).
            6) Close with the standard formula: “ΓΙΑ ΤΟΥΣ ΛΟΓΟΥΣ ΑΥΤΟΥΣ… ΜΗΝΥΩ…” and a signature block.
            7) Do NOT fabricate facts. If something critical is missing, ask targeted follow-up questions (in Greek) before including it.


            === OUTPUT TEMPLATE (headings may be adapted, content must remain in Greek) ===
            ΠΡΟΣ: Τον/Την κ. Εισαγγελέα Πρωτοδικών […/πόλη]
            Του μηνυτή: [Ονοματεπώνυμο], [Δ/νση], [Τηλέφωνο], [Email]
            Κατά: [Ονοματεπώνυμο/Επωνυμία] (αν γνωστός), [Στοιχεία επικοινωνίας/IBAN] (αν διαθέσιμα)

            I. Αντικείμενο
            Σύντομη περίληψη της καταγγελίας.

            II. Πραγματικά περιστατικά (Χρονολογική παράθεση)
            1) [Ημερομηνία]: [Γεγονός…]
            2) [Ημερομηνία]: [Γεγονός…]
            […]
            Συναλλαγές:
            - [#1] Ημερ.: […], Ποσό: [… €], Τρόπος/IBAN: […], Αναφορά: […]
            - [#2] […]

            III. Αποδεικτικά μέσα
            1) [Screenshots/Αποδείξεις/Συνομιλίες] — περιγραφή
            2) […]
            URLs/Emails/Τηλέφωνα (απαρίθμηση):
            - URL: […]
            - Email: […]
            - Τηλ.: […]

            IV. Νομική θεμελίωση
            Τα ανωτέρω συγκροτούν τα αδικήματα της απάτης (άρθρο 386 ΠΚ) και/ή απάτης με υπολογιστή (άρθρο 386Α ΠΚ), ενδεχομένως κατ’ εξακολούθηση, βάσει των επαναλαμβανόμενων πράξεων.

            V. Αιτήματα
            1) Να διαταχθεί προκαταρκτική εξέταση/προανάκριση και ψηφιακή διερεύνηση από τη Διεύθυνση Δίωξης Ηλεκτρονικού Εγκλήματος.
            2) Να αναζητηθούν στοιχεία κατόχων λογαριασμών/IBAN, IP addresses, πάροχοι, και να ληφθούν οι νόμιμες δικονομικές ενέργειες.
            3) Να ασκηθεί ποινική δίωξη κατά των υπαιτίων.
            4) Να μου κοινοποιούνται οι εξελίξεις στη δηλωθείσα διεύθυνση/email.

            VI. Συνημμένα
            1) [Τίτλος αποδεικτικού #1]
            2) […]

            Ημερομηνία: [..../..../....] – Τόπος: […]
            Ο Μηνυτής
            [Υπογραφή]

            === CONTEXT AVAILABLE ===
            - Reference documents (must be leveraged): {documents}
            - Conversation history (for missing data & context): {conversation_history}
            - Latest user message: {query}

            === DECISION LOGIC ===
            • If critical items from DATA NEEDED are missing, ask targeted follow-ups (in Greek) and do NOT produce the final complaint yet.
            • Otherwise, produce the complete complaint using the OUTPUT TEMPLATE.

            Generate your answer in {language}.
            
            """.format(documents=texts, conversation_history=request_data['conversation_history'],query=request_data['message'],language=language)

        
        messages = build_messages(prompt,file_list)

        print(messages)

        async def generate():
            try:
                async for chunk in model.astream(messages):
                    content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                    yield f"data: {json.dumps({'response': content, 'status': 200})}\n\n"

            except Exception as e:
                # Log error details            
                # OR raise it, if you don't want partial yield
                raise HTTPException(status_code=500, detail="Internal Server Error during LLM generation.")
            
        return StreamingResponse(generate(), media_type="text/event-stream")


    if request_data['conversation_type'] == 'normal':

        prompt = """
            You are a highly competent legal assistant designed to provide accurate, well-reasoned, and context-aware answers to legal questions. Your responses should be clear, concise, and grounded in the provided legal context and conversation history.

            Your task is to analyze the question posed by the user and generate a helpful answer based on the information available. If necessary, synthesize knowledge from both legal documents and prior conversation to ensure completeness and legal soundness.

            You have access to the following sources of information:

            1. **Legal Context**: This includes relevant legal texts, regulations, court decisions, or authoritative commentary provided as context. Use this as your primary source of legal truth.
                
                CONTEXT: {summarized_context}

            2. **User's Current Question**: This is the specific legal inquiry that you must address:
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
        app_workflow = request.app.state.app
        llm_params = pipeline.run_full_pipeline(request_data['message'],request_data['conversation_history'],app_workflow,web_search_activation=request_data['web_search_tool'])        

        if isinstance(llm_params, dict):
            
            prompt = prompt.format(**llm_params)

            # llm_params['conversation_history'] = request_data['conversation_history'] if len(request_data['conversation_history'])!=0 else []
            async def generate():
                try:
                    async for chunk in model.astream(prompt):
                        content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                        yield f"data: {json.dumps({'response': content, 'status': 200})}\n\n"

                except Exception as e:
                    # Log error details            
                    # OR raise it, if you don't want partial yield
                    raise HTTPException(status_code=500, detail="Internal Server Error during LLM generation.")
                
            return StreamingResponse(generate(), media_type="text/event-stream")
        elif isinstance(llm_params, str):
            async def fake_stream():
                yield f"data: {json.dumps({'response': llm_params, 'status': 200})}\n\n"

            return StreamingResponse(fake_stream(), media_type="text/event-stream")
        else:
            raise HTTPException(status_code=500, detail="Unexpected pipeline output.")
        
@router.post('/logout')
async def logout(response:Response):
    try:
        response.delete_cookie(key = "token")
        return True
    except HTTPException as e:
        raise HTTPException(status_code=403, detail=e.detail) 

