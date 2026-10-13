import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api.router import api_router
from app.core.websocket_manager import ws_manager
from app.services.reminder_engine import start_reminder_worker
from app.core.seeder import seed_database

# Auto-create tables for instant SQLite database generation
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Setup - Allow all origins for robust local multi-port WebSocket connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    # Seed database if empty
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
        
    asyncio.create_task(start_reminder_worker())

@app.websocket("/api/v1/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket connection error for user {user_id}: {e}")
        ws_manager.disconnect(websocket, user_id)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "developer_mode": True
    }
