import os

# --- Project Structure Definition ---
project_name = "trader-dashboard"

folders = [
    f"{project_name}/app",
    f"{project_name}/app/api",
    f"{project_name}/app/services",
    f"{project_name}/app/models",
    f"{project_name}/frontend",
    f"{project_name}/data"
]

# --- File Contents ---
files = {
    # 1. Root Files
    f"{project_name}/requirements.txt": """fastapi\nuvicorn\nlangchain-core\nlangchain-ollama\nlangchain-google-genai\nlangchain-community\nsqlalchemy\npandas\n""",
    f"{project_name}/.env": """GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE\nUSE_MOCK=True\n""",
    
    # 2. App Config & Main
    f"{project_name}/app/__init__.py": "",
    f"{project_name}/app/config.py": """import os\nfrom dotenv import load_dotenv\n\nload_dotenv()\n\nGOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")\nUSE_MOCK = os.getenv("USE_MOCK", "True").lower() == "true"\nDB_URI = "sqlite:///../data/out.db"\n""",
    f"{project_name}/app/main.py": """from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\nfrom app.api import chat\n\napp = FastAPI(title="Trader Dashboard API")\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=["*"],\n    allow_credentials=True,\n    allow_methods=["*"],\n    allow_headers=["*"],\n)\n\n# Include routers\napp.include_router(chat.router, prefix="/api")\n\nif __name__ == "__main__":\n    import uvicorn\n    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)\n""",
    
    # 3. Models Layer
    f"{project_name}/app/models/__init__.py": "",
    f"{project_name}/app/models/schemas.py": """from pydantic import BaseModel\n\nclass QueryRequest(BaseModel):\n    question: str\n\nclass QueryResponse(BaseModel):\n    status: str\n    answer: str\n    mode: str\n""",
    
    # 4. Services Layer (LangChain)
    f"{project_name}/app/services/__init__.py": "",
    f"{project_name}/app/services/agent.py": """from langchain_community.utilities import SQLDatabase\nfrom langchain_ollama import ChatOllama\nfrom langchain_google_genai import ChatGoogleGenerativeAI\nfrom langchain_community.agent_toolkits import create_sql_agent\nfrom app.config import USE_MOCK, DB_URI, GOOGLE_API_KEY\nimport os\n\n# Set API key for LangChain to pick up automatically\nos.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY\n\ndef get_agent():\n    db = SQLDatabase.from_uri(DB_URI)\n    \n    if USE_MOCK:\n        llm = ChatOllama(model="gemma2:2b", temperature=0)\n    else:\n        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)\n        \n    return create_sql_agent(llm, db=db, agent_type="tool-calling", verbose=True)\n""",
    
    # 5. API Routing Layer
    f"{project_name}/app/api/__init__.py": "",
    f"{project_name}/app/api/chat.py": """from fastapi import APIRouter, HTTPException\nfrom app.models.schemas import QueryRequest, QueryResponse\nfrom app.services.agent import get_agent\nfrom app.config import USE_MOCK\n\nrouter = APIRouter()\nagent_executor = get_agent()\n\n@router.post("/chat", response_model=QueryResponse)\nasync def chat_endpoint(request: QueryRequest):\n    try:\n        guardrails = "\\n\\nCRITICAL: Use tables 'funds' and 'daily_pnl'."\n        full_prompt = request.question + guardrails\n        \n        response = agent_executor.invoke({"input": full_prompt})\n        \n        return QueryResponse(\n            status="success",\n            answer=response["output"],\n            mode="Mock (Ollama)" if USE_MOCK else "Production (Gemini)"\n        )\n    except Exception as e:\n        raise HTTPException(status_code=500, detail=str(e))\n""",

    # 6. Frontend Files
    f"{project_name}/frontend/index.html": """<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <title>Trader Dashboard</title>\n    <script src="https://cdn.tailwindcss.com"></script>\n</head>\n<body class="bg-gray-950 text-white min-h-screen p-8">\n    <h1 class="text-2xl font-bold text-emerald-400 mb-4">Trader Dashboard UI</h1>\n    <p class="text-gray-400">See script.js for logic</p>\n    <script src="script.js"></script>\n</body>\n</html>\n""",
    f"{project_name}/frontend/script.js": """console.log("Frontend initialized and ready for FastAPI connection!");\n"""
}

def build_project():
    print(f"🚀 Building {project_name} structure...")
    
    # Create Folders
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"📁 Created: {folder}/")
        
    # Create Files
    for filepath, content in files.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 Created: {filepath}")

    print("\n✅ Project generation complete!")
    print(f"➡️  Next steps: Move your 'out.db' file into the '{project_name}/data/' folder!")

if __name__ == "__main__":
    build_project()