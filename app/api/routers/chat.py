from fastapi import APIRouter
from app.domain.schemas import ChatRequest
from app.adapters.groq_adapter import GroqAdapter

router = APIRouter()

# Dependency Injection
groq_client = GroqAdapter()

@router.post("")
def chat_endpoint(request: ChatRequest):
    """
    Primary Request Adapter for Chat stream.
    """
    result = groq_client.generate_text(messages=request.messages)
    
    # The frontend explicitly expects {"message": response} or {"error": e}
    if str(result).startswith("Error:"):
        return {"error": result}
    return {"message": result}
