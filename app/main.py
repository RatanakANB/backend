from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import chat, documentation, history
from app.adapters.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup SQLite tables completely fully automatically!
    await init_db()
    yield

app = FastAPI(
    title="VIBE Hexagonal Backend",
    description="Refactored using Ports and Adapters concept for high scalability and beginner-friendliness.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect Routes (Primary Driving Adapters)
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(documentation.router, prefix="/documentation-generator", tags=["Documentation"])
app.include_router(history.router, prefix="/history", tags=["History"])
