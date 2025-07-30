from fastapi import FastAPI, WebSocket, Cookie, WebSocketDisconnect
from backend.api.fast_api import router 
from backend.api.utils import verify_token
from fastapi.middleware.cors import CORSMiddleware
from backend.database.config.config import settings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging
from contextlib import asynccontextmanager
from backend.api.llm_pipeline import initialize_indexes,load_reranker_model,LLM_Pipeline

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Loading vector index")
    if settings.INIT_MODE == 'runtime':
        indexes = None
        cohere_client = None
        cohere_reranker = None
        while cohere_reranker==None:
            indexes = initialize_indexes(top_k=10)
            cohere_client,cohere_reranker = load_reranker_model()
        app.state.pipeline = LLM_Pipeline(indexes,cohere_reranker,cohere_client)
        app.state.app = app.state.pipeline.initialize_workflow()
        print("Vector index loaded")
    yield
    app.state.pipeline.shutdown()
    print("🛑 App shutting down...")

app = FastAPI(lifespan=lifespan)
logger = logging.getLogger("uvicorn")

url = settings.FRONTEND_URL

app.add_middleware(
    CORSMiddleware,
    allow_origins=[url],  # or your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)

app.mount('/assets',StaticFiles(directory='frontend/dist/assets', html=True), name='static')

@app.websocket('/ws')
async def websocket_endpoint(websocket:WebSocket, token: str = Cookie(None)):
    await websocket.accept()
    username = verify_token(token)
    if not username:
        await websocket.close(code=1008)
        return
    await websocket.send_text(f"Hello {username}! You are authenticated. ")
    try: 
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"You said: {data}")
    except WebSocketDisconnect:
        print(f"{username} Disconnected")

# ✅ Catch-all route for React Router (must come after mounting)
@app.get("/")
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str = ""):
    return FileResponse(os.path.join("frontend", "dist", "index.html"))


