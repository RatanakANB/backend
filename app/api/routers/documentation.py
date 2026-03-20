from fastapi import APIRouter, HTTPException
from app.domain.schemas import DocumentationRequest
from app.domain.services import DocumentationService
from app.adapters.groq_adapter import GroqAdapter
from app.adapters.sqlite_history_adapter import SQLiteHistoryAdapter

router = APIRouter()

# Dependency Injection
groq_client = GroqAdapter()
sqlite_history = SQLiteHistoryAdapter()
doc_service = DocumentationService(llm_client=groq_client, history_client=sqlite_history)

@router.post("")
async def documentation_generator_endpoint(request: DocumentationRequest):
    """
    Primary Request Adapter: Receives standard HTTP request, passes straight to Service Layer Domain Logic.
    """
    return await doc_service.generate_documentation(request)
