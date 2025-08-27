import litellm
# FORCE the global timeout for the litellm library to 30 minutes
litellm.timeout = 1800

import json
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
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

app = FastAPI(title="Financial Document Analyzer - Final Version")

def run_financial_crew(query: str, file_path: str):
    """Initializes and runs the financial analysis crew."""
    
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
    """Health check endpoint."""
    return {"message": "Financial Document Analyzer API is running"}

@app.post("/analyze")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights and risks.")
):
    """Analyzes a financial document and provides a comprehensive report."""
    
    file_id = str(uuid.uuid4())
    # Corrected: Check for '.pdf' files
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
        
    # Corrected: Save the input file as a '.pdf'
    file_path = f"data/financial_document_{file_id}.pdf"
    
    try:
        os.makedirs("data", exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        crew_output = run_financial_crew(query=query.strip(), file_path=file_path)
        final_result_string = str(crew_output)
        
        structured_output = {
            "query": query,
            "file_processed": file.filename,
            "analysis_result": final_result_string
        }
        
        os.makedirs("outputs", exist_ok=True)
        output_file_path = f"outputs/analysis_result_{file_id}.json"
        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(structured_output, f, indent=4)
            
        return structured_output
        
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