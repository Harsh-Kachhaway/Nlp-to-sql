from fastapi import APIRouter, HTTPException
import logging

# Import our exact data shapes
from app.models.schemas import QueryRequest, QueryResponse

# Import our AI Agent and Config
from app.services.agent import get_sql_agent
from app.config import USE_MOCK

# Setup a router instance
router = APIRouter()

# Setup logging so we can see errors in the terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the agent once when the server starts
# (This prevents loading the AI model from scratch on every single message)
agent_executor = get_sql_agent()

@router.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    """
    Receives a natural language question, passes it to the Text-to-SQL Agent,
    and returns the result.
    """
    if not agent_executor:
        raise HTTPException(
            status_code=500, 
            detail="AI Agent failed to initialize. Check database connection or API keys."
        )

    logger.info(f"Incoming Question: {request.question}")

    try:
        # 1. Add secret guardrails to keep the AI on track
        # This forces the model to stick to your specific tables
        guardrails = "\n\nCRITICAL AI INSTRUCTIONS:\n- Do NOT wrap SQL queries in markdown tags.\n- Give a clear, helpful final answer."
        full_prompt = request.question + guardrails
        
        # 2. Execute the LangChain workflow
        # .invoke() starts the ReAct loop (Thought -> Action -> Observation)
        response = agent_executor.invoke({"input": full_prompt})
        
        # 3. Format and return the successful response
        return QueryResponse(
            status="success",
            answer=response.get("output", "I processed the query but generated no output text."),
            mode="Mock (Ollama 2B)" if USE_MOCK else "Production (Gemini Flash)"
        )
        
    except Exception as e:
        logger.error(f"Agent Execution Error: {e}")
        # If the AI hallucinates bad SQL or crashes, we catch it gracefully 
        # and send a nice error message to the UI instead of crashing the server.
        raise HTTPException(
            status_code=500, 
            detail=f"The AI encountered an error processing your data: {str(e)}"
        )