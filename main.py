import litellm
litellm.timeout = 1800

import json
import sqlite3 # <-- Import Python's built-in SQLite library
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
from datetime import datetime # <-- Import datetime to timestamp our results
from crewai import Crew, Process

from agents import (
    data_quality_analyst,
    senior_financial_analyst,
    investment_advisor,
    risk_assessor
)
from task import (
    create_data_extraction_task,
    create_analysis_task,
    create_investment_advisory_task,
    create_risk_assessment_task
)

app = FastAPI(title="Financial Document Analyzer - Bonus Version")

# --- Database Setup ---
DB_FILE = "analysis_results.db"

def init_db():
    """Initializes the database and creates the results table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            query TEXT,
            result TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Initialize the database when the application starts
init_db()
# --- End of Database Setup ---


def run_financial_crew(query: str, file_path: str):
    # This function remains the same
    data_extraction_task = create_data_extraction_task(data_quality_analyst, file_path)
    analysis_task = create_analysis_task(senior_financial_analyst, context=[data_extraction_task])
    investment_advisory_task = create_investment_advisory_task(investment_advisor, context=[analysis_task])
    risk_assessment_task = create_risk_assessment_task(risk_assessor, context=[analysis_task])

    financial_crew = Crew(
        agents=[data_quality_analyst, senior_financial_analyst, investment_advisor, risk_assessor],
        tasks=[data_extraction_task, analysis_task, investment_advisory_task, risk_assessment_task],
        process=Process.sequential,
        verbose=True
    )
    
    result = financial_crew.kickoff(inputs={'query': query, 'file_path': file_path})
    return result

@app.get("/")
async def root():
    return {"message": "Financial Document Analyzer API is running"}

@app.post("/analyze")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights and risks.")
):
    file_id = str(uuid.uuid4())
    # Reverting to PDF for the final version
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
        
    file_path = f"data/financial_document_{file_id}.pdf"
    
    try:
        os.makedirs("data", exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        crew_output = run_financial_crew(query=query.strip(), file_path=file_path)
        final_result_string = str(crew_output)
        
        # --- Save result to SQLite Database ---
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO results (file_id, filename, query, result) VALUES (?, ?, ?, ?)",
            (file_id, file.filename, query, final_result_string)
        )
        conn.commit()
        conn.close()
        # --- End of Database Save ---
        
        # We can remove the JSON file saving now
        # os.makedirs("outputs", exist_ok=True)
        # ... (old json saving code removed)
            
        return {
            "status": "success",
            "message": "Analysis complete and result stored in the database.",
            "file_id": file_id,
            "analysis_result": final_result_string
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during processing: {str(e)}")
    
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Error removing file {file_path}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)