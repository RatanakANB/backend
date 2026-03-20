# VIBE Backend Development Guide

> **For Future Agentic AI Developers**: This document explains the architectural patterns and how to extend this codebase. Follow the Port & Adapter (Hexagonal Architecture) concepts strictly.

---

## 📐 Architecture Overview: Ports & Adapters (Hexagonal)

This backend uses **Hexagonal Architecture** (Ports & Adapters) to ensure:
- ✅ Easy swapping of external services (Groq → OpenAI → Local LLM)
- ✅ Beginner-friendly modular structure
- ✅ Clear separation of concerns
- ✅ Scalable to add databases, authentication, cache layers

### 🗂️ Folder Structure

```
app/
├── main.py                 # FastAPI app setup & middleware (ENTRY POINT)
├── core/                   # Configuration & global settings
│   ├── config.py           # Environment variables, secrets loading
│   └── __init__.py
├── ports/                  # INTERFACES (Contracts that adapters must fulfill)
│   ├── llm_port.py         # Abstract contract for any LLM (Groq, OpenAI, etc.)
│   ├── database_port.py    # [FUTURE] Database interface for SQLite/PostgreSQL
│   ├── auth_port.py        # [FUTURE] Authentication interface
│   └── __init__.py
├── adapters/               # CONCRETE IMPLEMENTATIONS (External service connectors)
│   ├── groq_adapter.py     # Groq API implementation of LLMPort
│   ├── openai_adapter.py   # [FUTURE] OpenAI implementation of LLMPort
   ├── database.py         # SQLite implementation with SQLAlchemy ORM
│   └── __init__.py
├── domain/                 # BUSINESS LOGIC (Core app logic, independent of frameworks)
│   ├── schemas.py          # Pydantic models (request/response validation)
│   ├── services.py         # Service layer (orchestrates adapters & business rules)
│   └── __init__.py
└── api/                    # PRIMARY ADAPTERS (HTTP layer - FastAPI routes)
    ├── routers/
    │   ├── chat.py         # /chat endpoint and logic
    │   ├── documentation.py # /documentation-generator endpoint and logic
    │   └── __init__.py
    └── __init__.py
```

---

## 🔄 Data Flow: Request → Response

### Example: Documentation Generation API Call

```
1. HTTP POST /documentation-generator
   ↓
2. [API Layer] documentation.py (FastAPI router)
   - Receives JSON request, validates with Pydantic schema
   ↓
3. [Service Layer] services.py (DocumentationService)
   - Builds prompts, orchestrates logic
   - Calls LLM through the PORT interface
   ↓
4. [Adapter Layer] groq_adapter.py (GroqAdapter)
   - Implements LLMPort contract
   - Actually calls external Groq API
   ↓
5. Response flows back through layers
   - Adapter returns text
   - Service formats it
   - Router returns JSON
   ↓
6. HTTP 200 + JSON response to frontend
```

---

## 💡 Core Concepts for Beginners

### What is a **Port**?
A **Port** is an interface (abstract class) that defines a contract.
- Example: `LLMPort` says "I need a `generate_text()` function"
- Any adapter that implements `LLMPort` must have `generate_text()`
- **Benefit**: You can swap Groq → OpenAI without touching your business logic

### What is an **Adapter**?
An **Adapter** is a concrete implementation of a Port.
- Example: `GroqAdapter` implements `LLMPort` by calling Groq's API
- Adapters handle all external service details (API keys, HTTP calls, etc.)
- **Benefit**: Business logic never knows about Groq SDK or HTTP

### What is a **Service**?
A **Service** is where your core business logic lives.
- Takes Ports injected (dependency injection)
- Builds prompts, formats responses, applies business rules
- Independent of FastAPI, databases, or Groq
- **Benefit**: Easy to unit test, reuse in CLI or other frameworks

---

## 🚀 Running the Backend

### Development Mode (Hot Reload)

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

**Result**: Server runs at `http://localhost:8000`
- FastAPI auto-docs: `http://localhost:8000/docs`
- Redoc docs: `http://localhost:8000/redoc`

### Production Mode

```bash
cd backend
uv run uvicorn app.main:app --port 8000
```

---

## 📝 How to Add New Features

### Scenario 1: Add a New Endpoint (Easy ✅)

**Goal**: Create a `/new-feature` endpoint that uses DocumentationService

**Steps**:
1. Create `app/api/routers/new_feature.py`
2. Import `DocumentationService` and `GroqAdapter`
3. Create FastAPI router with `@router.post("")`
4. Inject dependencies (adapter, service)
5. Call `service.method()` and return response
6. In `app/main.py`, add: `app.include_router(new_feature.router, prefix="/feature")`

**Example**:
```python
# app/api/routers/new_feature.py
from fastapi import APIRouter
from app.domain.schemas import MyRequest
from app.domain.services import MyService
from app.adapters.groq_adapter import GroqAdapter

router = APIRouter()
groq_client = GroqAdapter()
my_service = MyService(llm_client=groq_client)

@router.post("")
def my_feature_endpoint(request: MyRequest):
    return my_service.process(request)
```

### Scenario 2: Swap Groq for OpenAI (Medium 🟡)

**Goal**: Replace Groq with OpenAI without touching business logic

**Steps**:
1. Create `app/adapters/openai_adapter.py` that implements `LLMPort`
2. In routers, change:
   ```python
   # OLD
   groq_client = GroqAdapter()
   
   # NEW
   openai_client = OpenAIAdapter()
   
   my_service = MyService(llm_client=openai_client)  # Still works!
   ```
3. No changes needed to `DocumentationService` or business logic!

### Scenario 3: Add SQLite Database (Medium 🟡)

**Goal**: Persist chat history and docs to SQLite

**Steps**:
1. Create `app/ports/database_port.py`:
   ```python
   from abc import ABC, abstractmethod
   
   class DatabasePort(ABC):
       @abstractmethod
       def save_chat(self, user_id: str, message: str) -> None:
           pass
       
       @abstractmethod
       def get_chat_history(self, user_id: str) -> list:
           pass
   ```

2. Create `app/adapters/sqlite_adapter.py`:
   ```python
   from app.ports.database_port import DatabasePort
   import sqlite3
   
   class SQLiteAdapter(DatabasePort):
       def __init__(self, db_path: str = "vibe.db"):
           self.db_path = db_path
           self.conn = sqlite3.connect(db_path)
       
       def save_chat(self, user_id: str, message: str) -> None:
           # SQL insert logic here
           pass
       
       def get_chat_history(self, user_id: str) -> list:
           # SQL select logic here
           pass
   ```

3. In services, inject the database adapter:
   ```python
   class ChatService:
       def __init__(self, llm_client: LLMPort, db_client: DatabasePort):
           self.llm = llm_client
           self.db = db_client
       
       def handle_chat(self, user_id: str, message: str):
           self.db.save_chat(user_id, message)  # Use DB
           response = self.llm.generate_text(...)  # Use LLM
           return response
   ```

4. In routers, inject both:
   ```python
   llm_client = GroqAdapter()
   db_client = SQLiteAdapter()
   chat_service = ChatService(llm_client=llm_client, db_client=db_client)
   ```

### Scenario 4: Add JWT Authentication (Hard 🔴)

**Goal**: Protect endpoints with JWT tokens

**Steps**:
1. Create `app/ports/auth_port.py` with `verify_token()` and `create_token()` methods
2. Create `app/adapters/jwt_adapter.py` implementing the auth port
3. Create middleware in `app/core/middleware.py` that checks JWT for each request
4. In routers, use FastAPI Depends to inject auth requirement:
   ```python
   from fastapi import Depends
   
   def get_current_user(token: str = Depends(oauth2_scheme)):
       # Call auth adapter to verify
       return auth_adapter.verify_token(token)
   
   @router.post("")
   def protected_endpoint(current_user = Depends(get_current_user)):
       return {"user": current_user}
   ```

---

## 🧪 Testing Your Changes

### Quick Test: Manual API Call

```bash
# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'

# Test documentation endpoint
curl -X POST http://localhost:8000/documentation-generator \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello(): return \"world\"",
    "mode": "code_docs",
    "styles": []
  }'
```

### Unit Test Example

Create `tests/test_services.py`:

```python
from app.domain.services import DocumentationService
from app.ports.llm_port import LLMPort

class MockLLM(LLMPort):
    def generate_text(self, prompt: str = "", system_prompt: str = "", messages: list = None) -> str:
        return "Mock response"

def test_documentation_service():
    mock_llm = MockLLM()
    service = DocumentationService(llm_client=mock_llm)
    
    from app.domain.schemas import DocumentationRequest
    request = DocumentationRequest(code="print('hello')")
    result = service.generate_documentation(request)
    
    assert "documentation" in result
    assert result["documentation"] == "Mock response"
```

Run tests:
```bash
cd backend
uv run pytest tests/
```

---

## 📊 Dependency Injection Pattern (Key Concept!)

**Why use dependency injection?**

❌ **BAD** (Tightly coupled):
```python
class DocumentationService:
    def __init__(self):
        self.llm_client = GroqAdapter()  # Hard-coded!
    
    def generate_documentation(self, request):
        return self.llm_client.generate_text(...)  # Can't test, can't swap
```

✅ **GOOD** (Loosely coupled):
```python
class DocumentationService:
    def __init__(self, llm_client: LLMPort):  # Injected!
        self.llm_client = llm_client
    
    def generate_documentation(self, request):
        return self.llm_client.generate_text(...)  # Can test, can swap
```

**Benefits**:
- **Testing**: Pass a `MockLLM` instead of real Groq
- **Swapping**: Pass `OpenAIAdapter` instead of `GroqAdapter`
- **Flexibility**: Same service works with any adapter

---

## 🔧 Adding Environment Variables

1. Update `.env`:
   ```env
   GROQ_API_KEY=your_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   # DATABASE_URL=sqlite:///./docs.db
   # OPENAI_API_KEY=sk-...
   ```

2. In `app/core/config.py`, add the variable:
   ```python
   class Settings:
       GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
       DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vibe.db")
       # ...
   ```

3. Use in adapters:
   ```python
   from app.core.config import settings
   
   class GroqAdapter(LLMPort):
       def __init__(self):
           self.client = Groq(api_key=settings.GROQ_API_KEY)
   ```

---

## 🎯 Best Practices (Checklist)

- ✅ **Always use Ports**: Don't import adapters directly in services
- ✅ **Inject Dependencies**: Pass adapters to services via `__init__`
- ✅ **Separate Concerns**: Business logic in services, HTTP in routers, APIs in adapters
- ✅ **Use Pydantic Schemas**: Validate all inputs with type hints
- ✅ **Handle Errors Gracefully**: Return meaningful error messages
- ✅ **Document Complex Logic**: Add docstrings to services
- ✅ **Test with Mocks**: Use mock adapters for unit tests
- ✅ **Keep It DRY**: Reuse services and schemas across endpoints

---

## 🚨 Common Mistakes to Avoid

❌ **Mistake 1**: Import adapters in services
```python
# WRONG
from app.adapters.groq_adapter import GroqAdapter

class MyService:
    def __init__(self):
        self.llm = GroqAdapter()  # Can't swap, hard to test
```

✅ **Fix**: Inject adapters as ports
```python
# CORRECT
from app.ports.llm_port import LLMPort

class MyService:
    def __init__(self, llm_client: LLMPort):
        self.llm = llm_client  # Can swap, easy to test
```

---

❌ **Mistake 2**: Business logic in routers
```python
# WRONG
@router.post("")
def endpoint(request: DocumentationRequest):
    prompt = f"Generate docs for:\n{request.code}"  # Logic in router!
    response = groq_client.generate_text(prompt)
    return {"docs": response}
```

✅ **Fix**: Move logic to services
```python
# CORRECT
# app/domain/services.py
class DocumentationService:
    def generate_documentation(self, request: DocumentationRequest):
        prompt = f"Generate docs for:\n{request.code}"  # Logic here
        response = self.llm_client.generate_text(prompt)
        return {"docs": response}

# app/api/routers/documentation.py
@router.post("")
def endpoint(request: DocumentationRequest):
    return doc_service.generate_documentation(request)  # Clean router!
```

---

## 📈 Scaling Plan (Future Roadmap)

### Phase 1: Current (✅ Done)
- Groq LLM adapter
- Documentation & Chat endpoints
- Core business logic separated

### Phase 2: Database (🟡 Next)
- SQLite adapter with SQLAlchemy ORM
- Persist chat history & generated docs
- User workspace concept

### Phase 3: Authentication (🟡 Soon)
- JWT tokens for user identification
- Rate limiting per user
- API key management

### Phase 4: Multi-Model (🟡 Later)
- OpenAI adapter alongside Groq
- Model selection per request
- Cost tracking

### Phase 5: Advanced (🔴 Advanced Features)
- File upload support (PDF, images)
- Caching layer (Redis)
- Async processing queues (Celery)
- WebSocket chat streams

---

## 📞 How AI Agents Should Work With This Codebase

**When extending the backend, always:**

1. **Read the Port First**: Understand the contract in `app/ports/`
2. **Create an Adapter**: Implement the port in `app/adapters/`
3. **Use Dependency Injection**: Pass adapters to services
4. **Write Services**: Keep business logic in `app/domain/services.py`
5. **Create Routes**: Add endpoints in `app/api/routers/`
6. **Test with Mocks**: Write unit tests with mock adapters
7. **Update This Guide**: Document new patterns and gotchas

**Example Task for an AI Agent:**
> "Add an OpenAI adapter so we can support multiple LLMs"

**Agent Should**:
1. Create `app/adapters/openai_adapter.py` implementing `LLMPort`
2. Add `OPENAI_API_KEY` to `app/core/config.py`
3. Test it with same services (no changes needed)
4. Document in this file how to switch providers

---

## 🔗 Quick Links

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic Validation**: https://docs.pydantic.dev/
- **Groq API**: https://console.groq.com/
- **Hexagonal Architecture**: https://alistair.cockburn.us/hexagonal-architecture/

