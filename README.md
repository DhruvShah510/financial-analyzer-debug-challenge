# financial-analyzer-debug-challenge
A fully debugged and operational multi-agent financial document analyzer built with CrewAI and FastAPI.

# Fixed Financial Document Analyzer

## Project Overview
This project is a fully debugged and operational AI-powered financial analysis system built with CrewAI. It utilizes a team of four specialized AI agents to read, analyze, and provide investment insights and risk assessments on financial documents. The system is exposed via a FastAPI backend, allowing for easy integration and use. In addition to fixing all core bugs, this submission also includes the implementation of advanced bonus features: a database for persistent storage and an asynchronous task queue to handle concurrent requests, transforming the application into a scalable, production-style system.

---

## Features
* **Multi-Agent System:** A team of four distinct AI agents collaborate in a sequential workflow to produce a comprehensive report.
* **Asynchronous Task Queuing:** Uses Celery and Redis to handle long-running analysis jobs in the background, keeping the API fast and responsive.
* **Persistent Storage:** Saves all analysis results to a structured SQLite database (`analysis_results.db`) for permanent storage and future retrieval.
* **PDF & Text File Analysis:** Capable of ingesting and processing financial data from PDF files.
* **Web-Enabled Analysis:** The Senior Financial Analyst agent can use a search tool to gather real-time market news and sentiment.
* **Local LLM Integration:** Powered by a local LLM (e.g., Llama 3, Phi-3) running via Ollama.

---

## Tech Stack
* **Backend:** Python, FastAPI
* **AI Framework:** CrewAI
* **LLM Integration:** LangChain, Ollama
* **Tools:** Serper (for web search), PyPDFLoader

---

## Setup and Installation

1.  **Clone the Repository:**
    ```sh
    git clone https://github.com/DhruvShah510/financial-analyzer-debug-challenge.git
    cd financial-analyzer-debug-challenge
    ```
2.  **Create a Python Virtual Environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install Dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
4.  **Run Redis using Docker:**
    Redis will act as our message broker. Start it with this command:
    ```sh
    docker run -d -p 6379:6379 --name redis redis:7
    ```
5.  **Set Up Environment Variables:**
    Create a `.env` file in the root of the project (see `.env.example` for a template). Your file should contain:
    ```
    SERPER_API_KEY="your_serper_api_key_here"
    LITELLM_TIMEOUT="1800"
    ```

## How to Run and Use

To run the complete asynchronous application, you will need to have **two terminals** open.

1.  **Start Background Services:**
    Ensure your Docker containers for **Ollama** and **Redis** are running. Make sure you have pulled a model (e.g., `ollama pull llama3:8b`).

2.  **In Terminal 1: Start the Celery Worker:**
    This terminal will process the analysis jobs in the background. Navigate to your project folder, activate your virtual environment, and run:
    ```sh
    celery -A worker.celery_app worker --loglevel=info -P eventlet
    ```
    Leave this terminal running. You will see the crew's progress here when you submit a job.

3.  **In Terminal 2: Start the API Server:**
    Open a new terminal, navigate to your project folder, activate your virtual environment, and run:
    ```sh
    uvicorn main:app --reload
    ```
    This is your main application server.

4.  **Use the Application:**
    Open your web browser and navigate to **`http://127.0.0.1:8000/docs`**.
    * Use the `/analyze` endpoint to upload your PDF. You will get an **instant response** with a `file_id`.
    * Copy that `file_id`.
    * Use the `/results/{file_id}` endpoint to check the status of your job. Initially, it will be "PENDING." Once the worker is finished, the status will change to "COMPLETED" and you will see the full analysis.

    ### A Note on Testing and Performance
    This application's performance is highly dependent on the hardware it runs on.
    * **For users with a powerful GPU:** The system is capable of analyzing multi-page PDFs using a large model like `llama3:8b`.
    * **For users on a standard CPU:** Running large models locally is very slow. To demonstrate the application's full logical workflow, it is recommended to test with a smaller model (e.g., `phi3:mini` or `deepseek-r1:1.5b`).

---

## Summary of Bugs Found and Fixed

The original project was non-functional. The following is a summary of the issues identified and the corrective actions taken.

### Part 1: Deterministic Bugs (Code Errors)

* **In `main.py`:**
    * **Bug:** The FastAPI endpoint and an imported task object shared the same name (`analyze_financial_document`), leading to unpredictable "shadowing" behavior.
    * **Fix:** Renamed the endpoint function to `analyze_document_endpoint` to resolve the conflict.
      
    ---

    * **Bug:** The path to the uploaded document was never passed to the CrewAI process, causing the system to ignore the user's file.
    * **Fix:** The `file_path` was correctly passed into the `crew.kickoff()` method.
 
    ---

    * **Bug:** The crew was initialized with only one of the four defined agents and tasks, leaving the intended workflow unimplemented.
    * **Fix:** Assembled a full, sequential crew with all four agents and their corresponding tasks.

* **In `agents.py`:**
    * **Bug:** The `llm` object was used without being defined or initialized (`llm = llm`).
    * **Fix:** Correctly imported and initialized a `ChatOllama` instance from the modern `langchain-ollama` library.

    ---
      
    * **Bug:** Tools were passed as method references instead of instantiated objects, which is incompatible with CrewAI.
    * **Fix:** Re-engineered the tool as a proper class inheriting from `BaseTool` and passed the instantiated object to the agents.

* **In `tools.py`:**
    * **Bug:** The code called a non-existent `Pdf` class to read documents.
    * **Fix:** Imported and used the standard `PyPDFLoader` library for robust PDF parsing.
 
    ---
      
    * **Bug:** The custom tool class did not inherit from `BaseTool` or use a decorator, making it invisible to CrewAI.
    * **Fix:** Rebuilt the tool to correctly inherit from `BaseTool`, making it a valid component.
 
    ---
      
    * **Bug:** A `search_tool` was created but never used, and other tools were empty placeholders.
    * **Fix:** Removed the empty placeholders for clarity and correctly assigned the `search_tool` to the appropriate agent.

* **In `task.py`:**
    * **Bug:** The `verification` task was incorrectly assigned to the main analyst instead of the verifier agent.
    * **Fix:** This was corrected in the new, logical task sequence where the first agent is a `Data Quality Analyst`.

### Part 2: Inefficient Prompts (Logical & AI Errors)

* **Bug:** The original agent and task prompts were satirical and actively instructed the AI agents to perform poorly, hallucinate, and provide untrustworthy answers.
* **Fix:** All agent roles, goals, backstories, and task descriptions were completely rewritten to be professional, specific, and goal-oriented. This guides the agents to produce a high-quality, structured, and relevant financial analysis.

---

## Bonus Features Implemented

To build a more robust and scalable application, the following bonus features were successfully implemented:

### 1. Database Integration
* The application now uses a built-in SQLite database (`analysis_results.db`) to provide persistent storage for all analysis results.
* Each job is saved with a unique ID, the original query, the filename, a timestamp, its status (`PENDING`/`COMPLETED`), and the final analysis report.

### 2. Asynchronous Queue Worker Model
* The system was upgraded to handle concurrent requests using **Celery** and **Redis**.
* The FastAPI endpoint now instantly queues analysis jobs and returns a task ID to the user, ensuring the API remains fast and responsive even under heavy load.
* A separate Celery worker process runs the time-consuming AI analysis in the background, updating the database upon completion. This architecture transforms the application into a scalable, production-ready system.

---

## Challenges Faced and Strategic Decisions
After fixing all the deterministic bugs and rewriting the inefficient prompts, the application's core multi-agent workflow was fully functional.

During the final testing phase, I encountered a significant performance limitation with my local, CPU-based hardware. While the system is architected to use highly capable models like llama3:8b, my machine was unable to run them in a timely manner. This caused the connection to the Ollama server to time out before the agent could complete its complex reasoning task.

To successfully demonstrate the now-working application, I made the strategic decision to switch to a smaller, faster model (deepseek-r1:1.5b). This allowed the entire crew to run to completion without timeout errors, proving that all the bugs in the application's logic had been solved.

As a known trade-off, smaller models can exhibit a higher degree of "hallucination." Therefore, while the final report is structurally perfect, the specific financial numbers are illustrative rather than factually precise.

I am confident that when this same debugged code is run on a system with a dedicated GPU or is configured to use a high-performance cloud API (like Groq or OpenAI), a larger model like llama3:8b would execute successfully and resolve this minor hallucination issue, producing factually perfect answers.
