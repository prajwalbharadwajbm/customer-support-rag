from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.runnables import Runnable
from pydantic import BaseModel
import json
import re
from typing import AsyncGenerator, List
import logging
from dependencies import get_chain
from models.chat import ChatInput

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/stream")
async def chat_stream(
    chat_input: ChatInput, 
    chain: Runnable = Depends(get_chain)
):
    question = chat_input.messages[-1].content
    logger.info("Processing stream request with question: %s", question)
    
    return StreamingResponse(
        stream_generator(chain, question),
        media_type="text/event-stream"
    )    
    

async def stream_generator(chain: Runnable, question: str) -> AsyncGenerator[str, None]:
    """
    This function generates the AI response piece by piece (streaming).
    
    It also handles special "followup questions" that the AI might suggest.
    These are marked with << >> in the AI's response.
    
    Args:
        chain: The AI chain that generates responses
        question: The user's question
        
    Yields:
        String chunks of the response in a special format
    """
    
    # Variables to track what we're building
    followup_question_buffer = ""  # Stores text as we build followup questions
    content_buffer = ""           # Stores all content we've seen
    in_followup_question = False  # Flag to track if we're processing followup questions
  
    async for chunk in chain.astream({
        "question": question
    }):
        content_buffer += chunk           
        
        if isinstance(chunk, dict):
            content = chunk.get('answer', '')
            followup_question_buffer += content

            while True:                
                match = re.search(r"<<(.*?)>>", followup_question_buffer)
                if match:
                    pre_content = followup_question_buffer[:match.start()]                    
                    if pre_content.strip():
                        yield f"data: {json.dumps({'content': pre_content.strip()})}\n\n"
                    
                    followup_question = match.group(1).strip()
                    if followup_question:
                        followup_questions = followup_question.split("?>")
                        for question in followup_questions:
                            if question.strip():
                                yield f"data: {json.dumps({'followup_questions': [question.strip()]})}\n\n"

                    followup_question_buffer = followup_question_buffer[match.end():]                                       
                else:
                    break

            if not in_followup_question and followup_question_buffer.strip():
                yield f"data: {json.dumps({'content': followup_question_buffer.strip()})}\n\n"
                followup_question_buffer = ""
        else:     
            yield f"data: {json.dumps({'content': str(chunk)})}\n\n"
    
     
    if followup_question_buffer.strip():
        yield f"data: {json.dumps({'content': followup_question_buffer.strip()})}\n\n"
    yield "data: [DONE]\n\n"
                
            