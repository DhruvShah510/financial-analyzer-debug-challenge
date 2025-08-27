import os
from crewai.tools import BaseTool  # Corrected: BaseTool comes from the main 'crewai' library
from crewai_tools import SerperDevTool # Corrected: SerperDevTool comes from the 'crewai_tools' library
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the SerperDevTool for web searching
search_tool = SerperDevTool()

# --- Custom Tool for Reading Financial Documents (Class-based) ---

class FinancialDocumentTool(BaseTool):
    name: str = "Financial Document Reader Tool"
    description: str = "Reads the text content from a PDF financial document given its file path."

    def _run(self, file_path: str) -> str:
        """
        Reads the text content from a PDF financial document.
        """
        if not os.path.exists(file_path):
            return "Error: File not found at the specified path."
        
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()
            full_content = "".join(page.page_content for page in pages)
            
            if not full_content.strip():
                return "Error: Could not extract any text from the document. It might be empty or image-based."
            
            return full_content
        except Exception as e:
            return f"Error reading the PDF file: {e}"

# Instantiate the tool for use in our agents
read_document_tool = FinancialDocumentTool()