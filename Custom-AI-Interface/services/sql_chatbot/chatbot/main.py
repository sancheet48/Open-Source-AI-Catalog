from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_handler import LLMHandler

api = FastAPI()


class Query(BaseModel):
    question: str


@api.post("/query/")
async def get_query_response(query: Query):
    llm_handler = LLMHandler()
    try:
        response = llm_handler.get_response(query.question)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
