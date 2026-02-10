from fastapi import FastAPI
from app.routers.websocket import router

app = FastAPI(title="QrypTalk QKD Backend")

app.include_router(router)
