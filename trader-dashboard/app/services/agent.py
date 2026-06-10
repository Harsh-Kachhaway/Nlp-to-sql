import os
from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import create_sql_agent

from app.config import USE_MOCK, DB_URI, GOOGLE_API_KEY

# --- Configuration ---
# 1. Add your Google API Key here (or load it from a .env file)
# Set the key in the environment for LangChain
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# 2. THE TOGGLE: Set this to True to use Ollama, or False to use Gemini
USE_LOCAL_OLLAMA = False 

def get_sql_agent(db_path=DB_URI):
    """
    Creates and returns a LangChain SQL Agent connected to our database.
    It automatically switches between Ollama and Gemini based on the toggle.
    """
    
    # 1. Connect to the local SQLite database
    try:
        db = SQLDatabase.from_uri(db_path)
        print("✅ Database connected successfully.")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

    # 2. Select the LLM Engine
    if USE_LOCAL_OLLAMA:
        print("🤖 Booting Local Engine: Ollama (Mock/Testing Mode)")
        # Make sure you have pulled this model in your terminal: `ollama run gemma2:2b`
        llm = ChatOllama(
            model="sqlcoder", 
            # model="llama3.2:3b", 
            temperature=0
        )
    else:
        print("☁️ Booting Cloud Engine: Google Gemini (Production Mode)")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0
        )

    # 3. Create the Agent
    # We use verbose=True so you can see its exact thought process in the terminal
    agent_executor = create_sql_agent(
        llm=llm, 
        db=db, 
        agent_type="tool-calling", 
        verbose=True
    )
    
    return agent_executor

# --- Quick Local Testing ---
# If you run this file directly (instead of importing it), it will test the agent
if __name__ == "__main__":
    
    
    agent = get_sql_agent(DB_URI)
    
    if agent:
        print("\n--- Testing the Agent ---")
        question = "What tables are in this database?"
        
        # We append a safety string to ensure it behaves well
        safe_question = question + "\n\nCRITICAL: Do NOT use markdown formatting in your SQL queries."
        
        try:
            response = agent.invoke({"input": safe_question})
            print(f"\nFinal Answer: {response['output']}")
        except Exception as e:
            print(f"\n❌ Agent execution failed: {e}")