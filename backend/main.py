from fastapi import FastAPI, WebSocket, Cookie, WebSocketDisconnect
from backend.api.fast_api import router 
from backend.api.utils import verify_token
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.database.config.config import settings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging

app = FastAPI()
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
    print(username)
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

# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         reload_dirs=[os.path.dirname(os.path.abspath(__file__))],
#         reload_excludes=[".env", "requirements.txt", "main.py", "api/utils.py", "api/fast_api.py", "api/__init__.py","*/.git/*",
#             "*/__pycache__/*",
#             "*.pyc",
#             "*/.pytest_cache/*",
#             "*/.vscode/*",
#             "*/.idea/*"],
#         reload_delay=1,
#         reload_includes=["*.py", "*.html", "*.css", "*.js"]
#     )
