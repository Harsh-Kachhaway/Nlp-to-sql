from fastapi import APIRouter, HTTPException
import logging
from sqlalchemy import create_engine, inspect

# Import our exact data shapes
from app.models.schemas import QueryRequest, QueryResponse

# Import our AI Agent and Config
from app.services.agent import get_sql_agent
from app.config import USE_MOCK

# FIX: Import the unified configuration
from app.config import USE_MOCK, DB_URI

# Setup a router instance
router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

agent_executor = get_sql_agent()

# --- NEW: Dynamic Schema Generator ---
def get_dynamic_schema():
    """
    Instantly reads the live SQLite database and generates a text map 
    of all tables and columns to feed to the AI.
    """
    try:
        # engine = create_engine("sqlite:///out.db")
        engine = create_engine(DB_URI)
        inspector = inspect(engine)
        
        schema_text = "CURRENT DATABASE SCHEMA:\n"
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            col_names = [col['name'] for col in columns]
            schema_text += f"- Table '{table_name}' has columns: {', '.join(col_names)}\n"
            
        return schema_text
    except Exception as e:
        logger.error(f"Failed to read schema: {e}")
        return "Schema unavailable. Rely on agent tools."
# -------------------------------------

@router.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    if not agent_executor:
        raise HTTPException(status_code=500, detail="AI Agent failed to initialize.")

    logger.info(f"Incoming Question: {request.question}")

    try:
        # 1. Generate the live map of the database
        live_schema = get_dynamic_schema()
        
        # 2. Inject the live map into the secret AI instructions
        # This forces the AI to skip the "discovery" phase and write SQL immediately!
        guardrails = f"""
        \n\nCRITICAL AI INSTRUCTIONS:
        {live_schema}
        - Write the SQL query immediately to answer the user's question. 
        - Do NOT use tools to check the database tables or schema first, you already have the map above.
        - Do NOT wrap SQL queries in markdown tags.
        - Give a clear, helpful final answer.
        """
        
        full_prompt = request.question + guardrails
        
        # 3. Execute the LangChain workflow
        response = agent_executor.invoke({"input": full_prompt})
        
        # 4. Extract the raw output safely
        raw_output = response.get("output", "No output generated.")
        
        # Convert Lists/Blocks to a strict String for Pydantic
        final_string_answer = ""
        if isinstance(raw_output, list):
            text_chunks = []
            for item in raw_output:
                if isinstance(item, dict) and "text" in item:
                    text_chunks.append(item["text"])
                elif isinstance(item, str):
                    text_chunks.append(item)
            final_string_answer = "\n".join(text_chunks)
        else:
            final_string_answer = str(raw_output)
        
        # 5. Format and return the successful response
        return QueryResponse(
            status="success",
            answer=final_string_answer,
            mode="Mock (Ollama 2B)" if USE_MOCK else "Production (Gemini Flash)"
        )
        
    except Exception as e:
        logger.error(f"Agent Execution Error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"The AI encountered an error processing your data: {str(e)}"
        )