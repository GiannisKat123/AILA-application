from datetime import datetime
from jose import jwt, JWTError
from backend.database.config.config import settings
import json, re
from fastapi import HTTPException, Form, Response
from typing import Optional, List
from json_repair import repair_json

def create_access_token(data:dict,option:str='cookie'):
    """
    Create an access token with an expiration time.
    """
    if option == 'cookie': expiration_time = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    if option == 'verification': expiration_time = settings.VERIFICATION_TOKEN_EXPIRE_MINUTES
    encoding = data.copy()
    expires = int(datetime.now().timestamp()) + (int(expiration_time) * 60)
    encoding.update({"exp":expires})
    return jwt.encode(encoding,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def verify_token(token:str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get('sub')
    except JWTError as e:
        print(e)
        return None
    
async def parse_message_form(
    message: Optional[str] = Form(None),
    conversation_type: Optional[str] = Form(None),
    web_search_tool: Optional[str] = Form(None),
    conversation_history: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None)
) -> dict:
    """Parse and validate multipart/form-data for /request.

    Validates:
        - presence: message, conversation_type
        - web_search_tool: coerces to bool (1/true/yes/on)
        - conversation_history: JSON array (defaults to [])
        - conversation_id: The id of the conversation

    Returns:
        dict with normalized fields ready for downstream use.

    Raises:
        400 with specific detail on validation errors.
    """
    # Validate presence
    missing = [k for k,v in {
        "message": message,
        "conversation_type": conversation_type,
        "conversation_id": conversation_id
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
        "conversation_id": conversation_id
    }

def merge_dicts(dict1:dict,dict2:dict) -> dict:
    merged = dict1.copy()
    for k,v in dict2.items():
        if k in merged and isinstance(merged[k],dict) and isinstance(v,dict): merged[k] = merge_dicts(merged[k],v)
        else:merged[k] = v
    return merged

def lc_text_from_content(content:str|List) -> str:
    # LangChain AIMessage.content can be str OR a list of parts
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # keep only text parts
        return "".join(p.get("text","") for p in content if isinstance(p, dict) and p.get("type")=="text")
    return str(content)

def parse_llm_json(resp:Response) -> dict:
    raw = lc_text_from_content(resp.content).strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\n", "", raw)
        raw = re.sub(r"\n```$", "", raw)
    try: return json.loads(raw)
    except json.JSONDecodeError:
        try: return json.loads(repair_json(raw))
        except Exception as e: raise ValueError(f"Failed to parse LLM JSON: {e}\n Raw :\n {raw[:500]}")

    
