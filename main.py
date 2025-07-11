from google.genai import types
from root_agent.agent import create_chatbot_agent
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
import asyncio
import tempfile
import os
from pathlib import Path
from tools.file_parser import FileParserTool
from tools.memory_tool import set_runner

load_dotenv()

# --- Constants ---
APP_NAME = "KDM_Student_Onboarding"
USER_ID = "user123"  # A default user ID

# --- Agent and Runner Initialization ---
# Create a single agent instance using the existing root agent
chatbot_agent = create_chatbot_agent(USER_ID)

# The Runner is the correct way to execute an ADK agent.
# We use InMemorySessionService for session management and InMemoryMemoryService for conversation memory
runner = Runner(
    agent=chatbot_agent,
    app_name=APP_NAME,
    session_service=InMemorySessionService(),
    memory_service=InMemoryMemoryService(),  # Enable conversation memory for context sharing
)

# Initialize memory tool with runner for agent access
set_runner(runner)

async def ensure_session_exists(session_id):
    """Ensure session exists in the session service and add it to memory."""
    try:
        session = await runner.session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
        if not session:
            session = await runner.session_service.create_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=session_id
            )
        
        # Add session to memory service for context sharing between agents
        if runner.memory_service and session:
            await runner.memory_service.add_session_to_memory(session)
            
    except Exception as e:
        print(f"Session creation error: {e}")
        # Create session anyway
        session = await runner.session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
        # Add to memory service
        if runner.memory_service and session:
            await runner.memory_service.add_session_to_memory(session)

def call_agent(query, session_id, is_file=False):
    """Calls the agent using the runner and returns the final response."""
    try:
        # Ensure session exists using async
        asyncio.run(ensure_session_exists(session_id))
        
        if is_file:
            # Handle file upload
            processed_content = process_uploaded_file(query)
            if processed_content is None:
                return "Sorry, I couldn't process the uploaded file. Please ensure it's a valid PDF."
            query_text = processed_content
        else:
            query_text = query
        
        content = types.Content(role="user", parts=[types.Part(text=query_text)])
        
        # The runner needs a user_id and session_id for its internal logic.
        events = runner.run(user_id=USER_ID, session_id=session_id, new_message=content)

        for event in events:
            if event.is_final_response():
                return event.content.parts[0].text
        return "Sorry, I couldn't get a response."
    except Exception as e:
        # This will now print the detailed error to the console.
        print(f"Error calling agent: {e}")
        return f"Sorry, I encountered an error: {e}"

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text content."""
    try:
        # Create a temporary file to save the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        
        # Reset file pointer for potential future reads
        uploaded_file.seek(0)
        
        # Initialize file parser
        parser = FileParserTool()
        
        # Parse the document
        result = parser.parse_document(temp_file_path)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        if result["success"] and result["text_content"]:
            # Create a structured message for the document digitiser agent
            file_content = f"""DOCUMENT_UPLOAD_REQUEST:
Filename: {uploaded_file.name}
File Type: PDF
Page Count: {result.get('page_count', 'Unknown')}

EXTRACTED_CONTENT:
{result['text_content']}

PROCESSING_INSTRUCTION: Please process this document using the document digitiser agent to extract and store relevant user information. Check if the user has provided their phone number in previous messages, and if not, ask for it before proceeding with data storage."""
            
            return file_content
        else:
            print(f"File parsing errors: {result.get('parsing_errors', [])}")
            return None
            
    except Exception as e:
        print(f"Error processing uploaded file: {e}")
        return None

if __name__ == "__main__":
    print("KDM Chatbot is ready! Type 'exit' to end the conversation.")
    session_id = "test_session"
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = call_agent(user_input, session_id)
        if response:
            print("KDM Assistant:", response)
