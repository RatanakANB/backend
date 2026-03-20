import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Core Configuration
    Beginners: This file loads all secret keys and global settings from the .env file.
    If you add SQLite tracking or Auth URLs later, add the variables here!
    """
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    # DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vibe.db")

settings = Settings()
