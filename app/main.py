# app/main.py
#
# This is the FastAPI entrypoint for the Tech Explanation Service.
# It exposes a single POST endpoint "/explain" that returns
# a structured technical explanation for a given topic.
#
# Responsibilities:
# - Accept HTTP requests
# - Validate input using Pydantic schemas
# - Call the service layer
# - Return the AI-generated explanation in JSON format

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.tech_explanation_service import TechExplanationService

app = FastAPI(
    title="Tech Explanation Service",
    description="A portfolio-ready service demonstrating structured prompting and few-shot techniques with LangChain",
    version="0.1.0",
)

# Initialize the service once
service = TechExplanationService()


# --- Request/Response schema definitions ---
class ExplainRequest(BaseModel):
    topic: str


class ExplainResponse(BaseModel):
    explanation: str


# --- API Endpoint ---
@app.post("/explain", response_model=ExplainResponse)
async def explain_topic(request: ExplainRequest):
    """
    POST /explain

    Request:
        {
            "topic": "Your topic here"
        }

    Response:
        {
            "explanation": "AI-generated explanation"
        }
    """
    try:
        # Call the service layer to generate the explanation
        result = service.explain(request.topic)
        return ExplainResponse(explanation=result)
    except Exception as e:
        # Return a 500 HTTP error in case of unexpected exceptions
        raise HTTPException(status_code=500, detail=str(e))
