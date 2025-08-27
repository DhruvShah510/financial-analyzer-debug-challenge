import sqlite3
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
import os
import uuid

# Import our new Celery task
from worker import run_analysis_task

app = FastAPI(title="Financial Document Analyzer - Queue Version")

DB_FILE = "analysis_results.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Add a 'status' column to our table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL UNIQUE,
            filename TEXT NOT NULL,
            query TEXT,
            status TEXT,
            result TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.post("/analyze")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights and risks.")
):
    """
    Accepts a document, saves it, and queues it for analysis.
    Returns immediately with a task ID.
    """
    file_id = str(uuid.uuid4())
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
        
    file_path = f"data/financial_document_{file_id}.pdf"
    
    os.makedirs("data", exist_ok=True)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 1. Create a record in the DB with a "PENDING" status
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results (file_id, filename, query, status) VALUES (?, ?, ?, ?)",
        (file_id, file.filename, query, "PENDING")
    )
    conn.commit()
    conn.close()

    # 2. Send the job to the Celery worker
    run_analysis_task.delay(file_id, query, file_path, file.filename)

    # 3. Respond immediately to the user
    return {
        "message": "Analysis has been queued. Check the status using the /results/{file_id} endpoint.",
        "file_id": file_id
    }

@app.get("/results/{file_id}")
async def get_result(file_id: str):
    """Checks the database for the result of a given analysis task."""
    conn = sqlite3.connect(DB_FILE)
    # This allows us to get column names from the query result
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM results WHERE file_id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(status_code=404, detail="File ID not found.")
    
    # Return the database row as a dictionary
    return dict(row)