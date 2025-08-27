from crewai import Task
# Use the new tool name in the import statement
from tools import read_document_tool, search_tool

# --- Task Definitions ---

# Task 1: Data Extraction Task
def create_data_extraction_task(agent, file_path):
    return Task(
        description=f"""
        Read and extract the text content from the financial document located at: {file_path}.
        Focus on extracting all text accurately. If the document cannot be read or is empty,
        you must report this as the final answer. Do not proceed with a blank document.
        """,
        expected_output="The full, raw text content of the financial document. No analysis yet.",
        agent=agent,
        # Use the new tool name here as well
        tools=[read_document_tool]
    )

# Task 2: Financial Analysis Task
# The Senior Analyst takes the raw text and analyzes it.
def create_analysis_task(agent, context):
    return Task(
        description="""
        Analyze the provided text from the financial document. Perform a thorough analysis covering:
        1.  Key financial metrics (Revenue, Net Income, EPS, etc.).
        2.  Year-over-year growth trends.
        3.  Potential red flags or inconsistencies.
        4.  The company's overall financial health.
        
        Use the search tool to find current market news and sentiment related to the company
        to add relevant, up-to-date context to your analysis.
        """,
        expected_output="""
        A structured financial analysis report including:
        - A summary of the company's financial performance.
        - A list of key financial metrics and their trends.
        - A section on market context and sentiment.
        - A concluding paragraph on the company's financial health.
        """,
        agent=agent,
        context=context,
        tools=[search_tool]
    )

# Task 3: Investment Advisory Task
# The Investment Advisor works on the analysis to provide recommendations.
def create_investment_advisory_task(agent, context):
    return Task(
        description="""
        Based on the comprehensive financial analysis provided, formulate an investment thesis.
        Your final recommendation should be one of: Strong Buy, Buy, Hold, Sell, or Strong Sell.
        
        Justify your recommendation with at least three key points derived from the analysis.
        Consider the potential upside and downside.
        """,
        expected_output="""
        A clear, concise investment advisory note, containing:
        - The final investment recommendation (e.g., 'Buy').
        - A section with a detailed justification for the recommendation.
        - A brief overview of potential risks for the investor.
        """,
        agent=agent,
        context=context
    )

# Task 4: Risk Assessment Task
# The Risk Assessor also works on the analysis to identify risks.
def create_risk_assessment_task(agent, context):
    return Task(
        description="""
        Scrutinize the financial analysis report to identify and categorize potential risks.
        Look for market risks, credit risks, operational issues, and any competitive threats
        mentioned or implied in the data.
        """,
        expected_output="""
        A structured risk report including:
        - A list of identified risks, categorized by type.
        - An estimated severity for each risk (Low, Medium, High).
        - A brief description of why each item is considered a risk.
        """,
        agent=agent,
        context=context
    )