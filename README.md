# financial-analyzer-debug-challenge
A fully debugged and operational multi-agent financial document analyzer built with CrewAI and FastAPI.

# Fixed Financial Document Analyzer

## Project Overview
This project is a fully debugged and operational AI-powered financial analysis system built with CrewAI. It utilizes a team of four specialized AI agents to read, analyze, and provide investment insights and risk assessments on financial documents. The system is exposed via a FastAPI backend, allowing for easy integration and use.

---

## Features
* **Multi-Agent System:** A team of four distinct AI agents (Data Quality Analyst, Senior Financial Analyst, Investment Advisor, and Risk Assessor) collaborate in a sequential workflow to produce a comprehensive report.
* **PDF & Text File Analysis:** Capable of ingesting and processing financial data from both PDF and plain text files.
* **Web-Enabled Analysis:** The Senior Financial Analyst agent can use a search tool to gather real-time market news and sentiment for a more context-rich analysis.
* **Structured JSON Output:** The final report is saved in a structured, machine-readable JSON format for easy use in other applications.
* **Local LLM Integration:** Powered by a local LLM (e.g., Llama 3, Phi-3, etc.) running via Ollama, ensuring data privacy and control.

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
4.  **Set Up Environment Variables:**
    Create a `.env` file in the root of the project (see `.env.example` for a template). Your file should contain:
    ```
    SERPER_API_KEY="your_serper_api_key_here"
    ```

---

## How to Run and Use

1.  **Start Your Local LLM:**
    Ensure your local Ollama instance (e.g., via Docker) is running. Make sure you have pulled a model (e.g., `ollama pull llama3:8b`).

2.  **Start the API Server:**
    ```sh
    uvicorn main:app --reload
    ```

3.  **Use the Application:**
    Open your web browser and navigate to **`http://127.0.0.1:8000/docs`**. You can use this interactive interface to upload a financial document and receive a full analysis.

    ### A Note on Testing and Performance
    This application's performance is highly dependent on the hardware it runs on.
    * **For users with a powerful GPU:** The system is capable of analyzing multi-page PDFs using a large model like `llama3:8b`.
    * **For users on a standard CPU:** Running large models locally is very slow. To demonstrate the application's full logical workflow without timeouts, it is recommended to test with a smaller model (e.g., `phi3:mini` or `deepseek-r1:1.5b`) or a simple `.txt` file containing a few paragraphs of financial text.

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
      
    * **Bug:** Tools were passed as method references instead of instantiated objects, which is incompatible with CrewAI.
    * **Fix:** Re-engineered the tool as a proper class inheriting from `BaseTool` and passed the instantiated object to the agents.

* **In `tools.py`:**
    * **Bug:** The code called a non-existent `Pdf` class to read documents.
    * **Fix:** Imported and used the standard `PyPDFLoader` library for robust PDF parsing.
      
    * **Bug:** The custom tool class did not inherit from `BaseTool` or use a decorator, making it invisible to CrewAI.
    * **Fix:** Rebuilt the tool to correctly inherit from `BaseTool`, making it a valid component.
      
    * **Bug:** A `search_tool` was created but never used, and other tools were empty placeholders.
    * **Fix:** Removed the empty placeholders for clarity and correctly assigned the `search_tool` to the appropriate agent.

* **In `task.py`:**
    * **Bug:** The `verification` task was incorrectly assigned to the main analyst instead of the verifier agent.
    * **Fix:** This was corrected in the new, logical task sequence where the first agent is a `Data Quality Analyst`.

### Part 2: Inefficient Prompts (Logical & AI Errors)

* **Bug:** The original agent and task prompts were satirical and actively instructed the AI agents to perform poorly, hallucinate, and provide untrustworthy answers.
* **Fix:** All agent roles, goals, backstories, and task descriptions were completely rewritten to be professional, specific, and goal-oriented. This guides the agents to produce a high-quality, structured, and relevant financial analysis.

---

## Limitations and Future Improvements
The debugged application successfully executes the multi-agent workflow and produces a structurally correct financial analysis. A known limitation of general-purpose LLMs is a tendency towards "hallucination" with specific numerical data. As such, the quantitative details in the generated report are illustrative of the system's logical output rather than being factually precise. Future work could involve implementing more advanced data extraction techniques (like RAG or function-calling) to improve factual accuracy.
