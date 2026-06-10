import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# --- 1. Dynamic Path Resolution ---
# This automatically calculates the absolute path to your main 'trader-dashboard' folder.
# This ensures that no matter where you run the script from, it always finds the database.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- 2. Load Environment Variables ---
# Looks for the .env file in the root folder and loads its contents
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

# --- 3. Core Settings ---

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# The AI Engine Toggle
# os.getenv returns strings. This safely converts "True", "true", or "1" from the .env into a Python boolean.
USE_MOCK = os.getenv("USE_MOCK", "True").lower() in ("true", "1", "t")

# Database Configuration
# Dynamically points to trader-dashboard/data/out.db
DB_FILE_PATH = os.path.join(BASE_DIR, "data", "out.db")
DB_URI = f"sqlite:///{DB_FILE_PATH}"

# --- 4. Application Constants ---
# You can store general app settings here for easy changing later
APP_NAME = "Trader Dashboard API"
APP_VERSION = "1.0.0"
DEBUG_MODE = True

# --- 5. Startup Validation (Safety Checks) ---
# If you try to run production mode without an API key, this catches the error 
# and stops the server immediately with a helpful message, rather than crashing later.
if not USE_MOCK and not GOOGLE_API_KEY:
    print("🚨 CONFIG ERROR: USE_MOCK is False, but GOOGLE_API_KEY is missing!")
    print("Please add your Gemini API key to the .env file.")
    sys.exit(1) 

if not os.path.exists(DB_FILE_PATH):
    print(f"⚠️ WARNING: Database file not found at {DB_FILE_PATH}")
    print("Make sure you moved your 'out.db' file into the 'data/' folder.")