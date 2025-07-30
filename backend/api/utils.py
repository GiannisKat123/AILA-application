from datetime import datetime
from jose import jwt, JWTError
from backend.database.config.config import settings

def create_access_token(data:dict):
    """
    Create an access token with an expiration time.
    """
    expiration_time = settings.ACCESS_TOKEN_EXPIRE_MINUTES
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
    
# def initialize_model():
#     #### For LLM open source models via Ollama
#     # llm_model = ChatOllama(
#     #     model = "deepseek-r1:1.5b",
#     #     base_url = os.getenv("OLLAMA_SERVER_URL"),
#     #     temperature = 0.7,
#     #     top_p = 1.0,
#     #     repeat_penalty = 1.0,
#     # )
#     # return llm_model
#     os.environ['OPENAI_API_KEY'] = settings.API_KEY
#     llm = OpenAI(streaming=True)
#     storage_context = StorageContext.from_defaults(persist_dir='backend/api/aila_indices')
#     index = load_index_from_storage(storage_context)
#     query_engine = index.as_query_engine(llm=llm,similarity_top_k=8)
#     return query_engine


