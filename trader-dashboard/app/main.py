
    
import io
import uvicorn
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

# Import application constants and settings from your detailed config
from app.config import APP_NAME, APP_VERSION, DEBUG_MODE
# Import the chat router module
from app.api import chat

# Initialize connection engine for Excel migrations
# Adjust the fallback URI if your DB file resides elsewhere
DB_URL = "sqlite:///out.db"
db_engine = create_engine(DB_URL)

# 1. Initialize the FastAPI Application
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    debug=DEBUG_MODE,
    description="A modular Text-to-SQL RAG engine for querying trading database architecture with data ingestion support."
)

# 2. Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],             # Allows requests from any local frontend file/Gradio client
    allow_credentials=True,
    allow_methods=["*"],             # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],             # Allows custom headers (like Content-Type)
)

# 3. Register Existing Application Routers
app.include_router(chat.router, prefix="/api", tags=["Chat Engine"])

# 4. New Data Ingestion Endpoint
@app.post("/api/upload-excel", tags=["Data Ingestion"])
async def upload_excel(
    file: UploadFile = File(...), 
    sheet_mappings: str = Form(default="")
):
    """
    Accepts an Excel binary workbook, processes multiple sheets, maps them to explicit 
    tables based on sheet_mappings string (e.g., 'Sheet1=funds, Sheet2=daily_pnl'), 
    normalizes dates/null values to 0, and pushes them to SQLite.
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file format. Please upload a valid Excel spreadsheet (.xlsx or .xls)."
        )
    
    try:
        # Parse the custom sheet mappings input string into a lookup dictionary
        # Input format: "Sheet1=funds, Sheet2=daily_pnl"
        mapping_dict = {}
        if sheet_mappings.strip():
            pairs = sheet_mappings.split(",")
            for pair in pairs:
                if "=" in pair:
                    sheet, table = pair.split("=")
                    mapping_dict[sheet.strip()] = table.strip()

        contents = await file.read()
        
        # FIX: Setting sheet_name=None forces pandas to read ALL sheets as a dictionary: {sheet_name: DataFrame}
        excel_sheets = pd.read_excel(io.BytesIO(contents), sheet_name=None)
        
        summary_results = []
        
        for sheet_name, df in excel_sheets.items():
            # Determine target table name: Use mapping override if provided, else fall back to sheet name
            target_table = mapping_dict.get(sheet_name, sheet_name.strip())
            
            # Safe Timestamp Conversion to Text Strings
            datetime_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns
            for col in datetime_cols:
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Clean Data: Empty/NaN entries cross-convert to absolute numerical 0s
            df = df.fillna(0)
            
            # Commit sheet to its specific SQLite table
            df.to_sql(target_table, con=db_engine, if_exists="append", index=False)
            
            summary_results.append({
                "sheet": sheet_name,
                "target_table": target_table,
                "rows": len(df)
            })
            
        return {
            "status": "success",
            "message": "Multi-sheet workbook successfully ingested.",
            "details": summary_results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Automated ingestion pipeline failed: {str(e)}"
        )

# 5. Root Health Check Endpoint
@app.get("/", tags=["System Overview"])
async def root_health_check():
    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION
    }

# 6. Programmatic Server Execution (Configured for Local Network Sharing)
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0",  # Broadens interface access for network sharing (phones, laptops, tablets)
        # host="127.0.0.1", 
        port=8000, 
        reload=True      # Hot-reloads your application whenever file modifications are saved
    )