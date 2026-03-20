from pydantic import BaseModel
from typing import List, Dict, Any

class DocumentationRequest(BaseModel):
    """
    Domain Schema: Validates the incoming JSON data from the React frontend for Code Docs
    """
    code: str
    styles: List[str] = []
    custom_style: str = ""
    mode: str = "code_docs"

class ChatRequest(BaseModel):
    """
    Domain Schema: Validates incoming Chat arrays.
    """
    messages: List[Dict[str, Any]]
