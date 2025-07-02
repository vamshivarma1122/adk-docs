import asyncio
import pandas as pd
from io import StringIO
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import FunctionTool, BuiltInCodeExecutor
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

# Define constants
GEMINI_2_FLASH = "gemini-2.0-flash"
APP_NAME = "artifact_code_executor_app"
USER_ID = "user_123"
SESSION_ID = "session_001"
CSV_FILENAME = "bank_statement.csv"

# --- 1. Prepare a dummy CSV file content ---
DUMMY_CSV_CONTENT = """Date,Description,Amount
2023-01-01,Groceries,-50.00
2023-01-02,Salary,2000.00
2023-01-03,Coffee,-5.00
2023-01-04,Utilities,-100.00
2023-01-05,Freelance Income,500.00
"""

# --- 2. Callback to save the artifact ---
async def upload_csv_to_artifact(callback_context: CallbackContext, **kwargs):
    """
    Saves a dummy CSV file as an artifact in the callback context.
    This callback runs before the model is called.
    """
    csv_bytes = DUMMY_CSV_CONTENT.encode('utf-8')
    csv_artifact = types.Part(
        inline_data=types.Blob(mime_type="text/csv", data=csv_bytes)
    )
    print(f"[{callback_context.agent_name}] Saving artifact '{CSV_FILENAME}'...")
    version = await callback_context.save_artifact(
        filename=CSV_FILENAME,
        artifact=csv_artifact
    )
    print(f"[{callback_context.agent_name}] Artifact '{CSV_FILENAME}' saved as version {version}.")

# --- 3. Custom Tool to Load Artifact and make it available to Code Executor ---
# This tool will be called by the agent to load the artifact's content.
@FunctionTool(name="get_bank_statement_csv", description="Loads the bank statement CSV artifact and returns its content as a string. Use this to get the raw CSV data for analysis.")
async def get_bank_statement_csv_tool(tool_context: ToolContext) -> str:
    """
    Loads the CSV artifact and returns its content as a string.
    The agent can then parse this string and use it with BuiltInCodeExecutor.
    """
    try:
        csv_artifact = await tool_context.load_artifact(filename=CSV_FILENAME)
        if csv_artifact and csv_artifact.inline_data:
            csv_content = csv_artifact.inline_data.data.decode('utf-8')
            return csv_content
        else:
            return f"Error: Artifact '{CSV_FILENAME}' not found. Please ensure it was uploaded."
    except Exception as e:
        return f"An unexpected error occurred while loading artifact '{CSV_FILENAME}': {e}"

# --- 4. Define the LlmAgent and run the example ---
async def main():
    # Initialize services
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService() # Crucial: Runner needs an artifact service

    # Define the LlmAgent
    llm_agent = LlmAgent(
        name="ArtifactCodeAgent",
        model=GEMINI_2_FLASH,
        description="""You are an expert at analyzing financial data.
        You have access to a tool named `get_bank_statement_csv` that will provide you with the content of the 'bank_statement.csv' file as a string.
        When performing calculations or data analysis, you must use the `BuiltInCodeExecutor` to execute Python code.
        Your workflow should be:
        1.  Call the `get_bank_statement_csv()` tool to retrieve the CSV content.
        2.  Once you have the CSV content string, use `pandas.read_csv(StringIO(csv_content_string))` in your Python code within the BuiltInCodeExecutor to load it into a DataFrame.
        3.  Perform the requested calculation or analysis on the DataFrame.
        4.  Provide the final answer and explain your steps, including the code used.
        """,
        code_executor=BuiltInCodeExecutor(), # BuiltInCodeExecutor itself does not need artifact_service directly here,
                                             # as the custom tool handles loading.
        tools=[get_bank_statement_csv_tool], # Register the custom tool
        before_model_callback=upload_csv_to_artifact # To save the artifact initially
    )

    runner = Runner(
        agent=llm_agent,
        app_name=APP_NAME,
        session_service=session_service,
        artifact_service=artifact_service # Essential: The Runner must be configured with an ArtifactService
    )

    print("Running agent to analyze bank statement expenses...")
    query_content = types.Content(role='user', parts=[types.Part(text="What is the total sum of all 'Amount' values in the bank statement CSV? Show your calculation using Python code.")])
    
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=query_content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("\n--- Agent Final Response ---\n", final_response)
        elif event.is_tool_code_event():
            print(f"\n--- Tool Code Event ---\nTool: {event.tool_code_event.tool_name}\nCode:\n'''\n{event.tool_code_event.code}\n'''")
        elif event.is_model_content_event():
            print(f"\n--- Model Content Event ---\n{event.model_content_event.contents[0].parts[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
