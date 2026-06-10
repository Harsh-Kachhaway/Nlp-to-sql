import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import application constants and settings from our detailed config
from app.config import APP_NAME, APP_VERSION, DEBUG_MODE
# Import the chat router module
from app.api import chat

# 1. Initialize the FastAPI Application
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    debug=DEBUG_MODE,
    description="A modular Text-to-SQL RAG engine for querying trading database architecture."
)

# 2. Configure CORS (Cross-Origin Resource Sharing)
# Since your frontend (index.html) runs on a different port/protocol than the API backend,
# this middleware ensures the browser allows them to communicate securely.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],             # Allows requests from any local frontend file
    allow_credentials=True,
    allow_methods=["*"],             # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],             # Allows custom headers (like Content-Type)
)

# 3. Register Application Routers
# This prefixes all chat endpoints with '/api', turning the route into: POST http://127.0.0.1:8000/api/chat
app.include_router(chat.router, prefix="/api", tags=["Chat Engine"])

# 4. Root Health Check Endpoint
# Useful for verifying the server is up and running independently of the AI systems.
@app.get("/", tags=["System Overview"])
async def root_health_check():
    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION
    }

# 5. Programmatic Server Execution
# Allows you to launch the server directly using 'python app/main.py' from the terminal.
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True  # Automatically reboots the server whenever you save code edits
    )