from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import posts, users, auth, websocket  # WebSocket импортирован
from .settings import settings

app = FastAPI(title="Blog API", version="6.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники для теста
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(websocket.router)  # <-- WebSocket роутер успешно добавлен!

@app.get("/")
def root():
    return {"xabar": "Blog API v6.0 — WebSocket bilan!"}

@app.get("/health")
def health():
    return {"status": "ok"}