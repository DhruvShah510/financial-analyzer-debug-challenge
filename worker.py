import os
import sqlite3
from celery import Celery
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

# --- Celery Configuration ---
# Corrected: Using the direct IP address for Redis instead of 'localhost'
celery_app = Celery(
    'tasks',
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0'
)
celery_app.conf.update(
    task_track_started=True,
)
# --- End of Celery Configuration ---

DB_FILE = "analysis_results.db"

@celery_app.task
def run_analysis_task(file_id: str, query: str, file_path: str, filename: str):
    """A Celery task to run the full CrewAI analysis and save the result."""
    
    # 1. Run the CrewAI financial crew
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
    
    crew_output = financial_crew.kickoff(inputs={'query': query, 'file_path': file_path})
    final_result_string = str(crew_output)

    # 2. Save the final result to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE results SET result = ?, status = 'COMPLETED' WHERE file_id = ?",
        (final_result_string, file_id)
    )
    conn.commit()
    conn.close()

    # 3. Clean up the temporary file
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error removing file {file_path}: {e}")
            
    return {"status": "Complete", "result": final_result_string}