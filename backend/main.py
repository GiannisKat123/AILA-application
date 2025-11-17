from contextlib import asynccontextmanager
from fastapi import FastAPI,WebSocket,Cookie,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.database.config.config import settings
from backend.api.llm_pipeline import initialize_indexes, load_reranker_model, LLM_Pipeline
from backend.api.fast_api import router
from backend.api.utils import verify_token
import logging, os

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("⚙️  Loading vector index...")
    pipeline = None

    if settings.INIT_MODE == 'runtime':
        indexes = None
        reranker = None
        top_k=10
        while reranker is None:
            indexes = initialize_indexes(top_k)
            reranker = load_reranker_model()
        pipeline = LLM_Pipeline(indexes,reranker,top_k)
        app.state.pipeline = pipeline
        app.state.app = pipeline.initialize_workflow()
        app.state.user_data_dict = {}
        print("✅ Vector index and pipeline loaded.")
    else:
        print(f"⏭️  Skipping runtime init (INIT_MODE={settings.INIT_MODE}).")

    try:
        yield
    finally:
        if hasattr(app.state, "pipeline") and app.state.pipeline is not None:
            app.state.pipeline.shutdown()
            print("🛑 Pipeline shutdown complete.")
        else:
            print("🛑 App shutting down (no pipeline to release).")

app = FastAPI(lifespan=lifespan)

logger = logging.getLogger('uvicorn')

url = settings.FRONTEND_URL

app.add_middleware(
    CORSMiddleware, allow_origins=[url],allow_credentials=True,allow_methods=['*'],allow_headers=['*']
)

app.include_router(router)

app.mount('/assets',StaticFiles(directory='frontend/dist/assets',html=True),name='static')

app.websocket('/ws')
async def websocket_endpoint(websocket:WebSocket,token:str=Cookie(None)):
    await websocket.accept()
    username = verify_token(token)
    if not username:
        await websocket.close(code=1008)
        return 
    await websocket.send_text(f"Hello {username}! You are authenticated")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"You said: {data}")
    except WebSocketDisconnect:
        print(f"{username} disconnected")

@app.get('/')
@app.get("/{full_path:path}")
async def serve_react_app(full_path:str=''):
    return FileResponse(os.path.join("frontend", "dist", "index.html"))
    