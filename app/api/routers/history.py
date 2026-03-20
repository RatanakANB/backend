from fastapi import APIRouter, HTTPException
from app.adapters.sqlite_history_adapter import SQLiteHistoryAdapter

router = APIRouter()

# Dependency Injection
sqlite_history = SQLiteHistoryAdapter()

@router.get("/docs/{history_id}")
async def get_docs_history_endpoint(history_id: str):
    """Retrieves previous GENERATE DOCS tasks."""
    res = await sqlite_history.get_docs_history(history_id)
    if not res:
        raise HTTPException(status_code=404, detail="History not found")
    return res

@router.get("/docs")
async def list_docs_history_endpoint():
    """Lists all GENERATE DOCS tasks sparsely."""
    return await sqlite_history.get_all_docs_history()

@router.delete("/docs/{history_id}")
async def remove_docs_history_endpoint(history_id: str):
    """Purges explicitly a specific GENERATE DOCS tasks safely."""
    success = await sqlite_history.delete_docs_history(history_id)
    if not success:
        raise HTTPException(status_code=404, detail="History not found")
    return {"status": "deleted"}

@router.get("/explain/{history_id}")
async def get_explain_history_endpoint(history_id: str):
    """Retrieves previous EXPLAIN tasks."""
    res = await sqlite_history.get_explain_history(history_id)
    if not res:
        raise HTTPException(status_code=404, detail="History not found")
    return res

@router.get("/explain")
async def list_explain_history_endpoint():
    """Lists all EXPLAIN tasks sparsely."""
    return await sqlite_history.get_all_explain_history()

@router.delete("/explain/{history_id}")
async def remove_explain_history_endpoint(history_id: str):
    """Purges explicitly a specific EXPLAIN output tasks securely."""
    success = await sqlite_history.delete_explain_history(history_id)
    if not success:
        raise HTTPException(status_code=404, detail="History not found")
    return {"status": "deleted"}

@router.delete("/rollback")
async def rollback_history_database_endpoint():
    """Drops securely all records instantly leaving a clean empty tabular structure."""
    return await sqlite_history.clear_all_history()
