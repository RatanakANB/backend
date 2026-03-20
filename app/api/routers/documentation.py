from fastapi import APIRouter
from app.domain.schemas import DocumentationRequest
from app.domain.services import DocumentationService
from app.adapters.groq_adapter import GroqAdapter

router = APIRouter()

# Dependency Injection for Adapters (Makes replacing Groq with another Provider incredibly easy later format-wise)
# Beginners: The router handles ONLY the web connection side of things (HTTP rules).
groq_client = GroqAdapter()
doc_service = DocumentationService(llm_client=groq_client)

@router.post("")
def documentation_generator_endpoint(request: DocumentationRequest):
    """
    Primary Request Adapter: Receives standard HTTP request, passes straight to Service Layer Domain Logic.
    """
    return doc_service.generate_documentation(request)
