from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from model import *
from helper import ResumeGraph
import json

app = FastAPI(title="Interview ai")

# Initialize ResumeGraph once at startup
resume_processor = ResumeGraph()
graph = resume_processor.graph  # Get the compiled graph

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_config(id: str) -> dict:
    """
    Create a configuration dictionary for the graph with the given thread ID.
    
    Args:
        id (str): The thread ID to use in the configuration
        
    Returns:
        dict: Configuration dictionary with thread ID
    """
    return {"configurable": {"thread_id": id}}

def resume_question(id: str) -> dict:
    """
    Generate the next interview question for a given thread ID.
    
    This function:
    1. Retrieves the current state for the thread
    2. Generates a new question using the ResumeGraph
    3. Updates the state with the new question
    4. Returns the latest question
    
    Args:
        id (str): The thread ID to generate a question for
        
    Returns:
        dict: A dictionary containing either:
            - {"question": str} with the generated question
            - {"error": str} if an error occurs
    """
    try:
        config = get_config(id)
        current_state_dict = graph.get_state(config).values
        
        # Initialize a new ResumeMode if no state exists
        if not current_state_dict:
            current_state = ResumeMode(
                resume_text="",
                work_experience_list=WorkExperienceList(work_experiences=[]),
                education_list=EducationList(education=[]),
                resume_insights=ResumeInsight(insights=[]),
                interview_question_list=[]
            )
        else:
            # Convert the dictionary to a ResumeMode object
            current_state = ResumeMode(
                resume_text=current_state_dict.get('resume_text', ''),
                work_experience_list=current_state_dict.get('work_experience_list', WorkExperienceList(work_experiences=[])),
                education_list=current_state_dict.get('education_list', EducationList(education=[])),
                resume_insights=current_state_dict.get('resume_insights', ResumeInsight(insights=[])),
                interview_question_list=current_state_dict.get('interview_question_list', [])
            )

        # Call the generate_question node function with the ResumeMode object
        updated_state = resume_processor.generate_question(current_state)

        # Update the state in the checkpointer
        graph.update_state(config, updated_state.dict(), as_node="generate_question")

        # Get the latest question
        if not updated_state.interview_question_list:
            return {"error": "No questions available"}
            
        latest_question = updated_state.interview_question_list[-1]
        return {"question": latest_question.question}
        
    except Exception as e:
        print(f"Error in resume_question: {str(e)}")
        return {"error": str(e)}

async def stream_response(message: str, id: str):
    """
    Stream the response from the conversation graph using Server-Sent Events (SSE).
    
    This function:
    1. Processes the input message through the graph
    2. Streams the results in real-time
    3. Formats the output as SSE events
    
    Args:
        message (str): The message to process
        id (str): The thread ID to use for state management
        
    Yields:
        str: SSE formatted events containing either:
            - Summary content
            - Generated questions
            - Error messages
    """
    try:
        config = get_config(id)
        async for event in graph.astream_events({"resume_text": message}, config, version="v2"):
            if event["event"] == "on_chat_model_stream" and (event['metadata'].get('langgraph_node') == 'summarizer' or event['metadata'].get('langgraph_node') == 'generate_question'):
                data = event["data"]
                content = data["chunk"].content

                # Format the response as SSE
                if event['metadata'].get('langgraph_node') == 'summarizer':
                    print("--------------------------------------babar-----------------------------------------------")
                    print(f"{content}")
                    print("--------------------------------------babar-----------------------------------------------")
                    yield f"data: {json.dumps({'summary': content})}\n\n"
                else:
                    yield f"data: {json.dumps({'question': content})}\n\n"
                
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.get("/resume_question")
async def resume(id: str = Query(..., description="Thread ID")):
    """
    Get the next interview question for a given thread ID.
    
    This endpoint:
    1. Takes a thread ID as a query parameter
    2. Generates a new question based on the current state
    3. Returns the question in JSON format
    
    Args:
        id (str): The thread ID to generate a question for
        
    Returns:
        dict: A dictionary containing either:
            - {"question": str} with the generated question
            - {"error": str} if an error occurs
    """
    return resume_question(id)

@app.get("/process_node")
async def process_node(
    id: str = Query(..., description="Thread ID"),
    message: str = Query(..., description="Message to process")
):
    """
    Process a message through the graph with streaming output.
    
    This endpoint:
    1. Takes a thread ID and message as query parameters
    2. Processes the message through the graph
    3. Streams the results in real-time using Server-Sent Events
    
    Args:
        id (str): The thread ID to use for state management
        message (str): The message to process
        
    Returns:
        StreamingResponse: A streaming response containing:
            - Summary content
            - Generated questions
            - Error messages
    """
    return StreamingResponse(
        stream_response(message, id),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )