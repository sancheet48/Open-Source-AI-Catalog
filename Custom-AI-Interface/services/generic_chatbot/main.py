from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from chatbot.llm_handler import LLMHandler

api = FastAPI()


class Message(BaseModel):
    User: Optional[str] = ""
    Assistant: Optional[str] = ""


class Query(BaseModel):
    question: str
    input_prompt: Optional[str] = (
        "You are a helpful assistant to answer the given question from the user."
    )
    temperature: Optional[float] = 0.2
    messages: List[Dict[str, Optional[str]]] = [{"User": "", "Assistant": ""}]
    repetition_penalty: Optional[float] = 1.1
    top_k: Optional[int] = 40
    top_p: Optional[float] = 0.95
    context_length: Optional[int] = 1024


@api.post("/query/")
async def get_query_response(query: Query):
    llm_handler = LLMHandler(
        input_prompt=query.input_prompt,
        temperature=query.temperature,
        repetition_penalty=query.repetition_penalty,
        top_k=query.top_k,
        top_p=query.top_p,
        context_length=query.context_length,
        messages=query.messages,
    )
    try:
        response = llm_handler.get_response(query.question)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
