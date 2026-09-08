from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.chat import router as chat_router 
from api.routes.command import router as command_router
from api.routes.voice import router as voice_router

from app_services.iris_service import iris_service

app = FastAPI(
    title="IRIS API",
    description="Backend API for the IRIS AI Assistant",
    version="2.0.0"
)

# CORS acts as the bridge for connecting the react frontend to the FastAPI's local host
# CORS tells the FastAPI to trust requests coming from the react frontend running at localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(command_router)
app.include_router(voice_router)

@app.get("/")
def root():
    return {
        "message": "IRIS API is running"
    }

@app.get("/api/health")
def health_check():

    database_connected = (
        iris_service.is_database_connected()
    )

    return {
        "status": "healthy",
        "backend": "online",
        "database": "connected"
        if database_connected
        else "disconnected"
    }