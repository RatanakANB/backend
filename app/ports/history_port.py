from abc import ABC, abstractmethod

class HistoryPort(ABC):
    """
    Port (Interface) handling persistence of App History.
    Beginners: This contract allows you to seamlessly switch databases
    later (like SQLite to MongoDB) by just writing a new Adapter.
    """
    
    @abstractmethod
    async def create_generate_docs_history(self, code: str, styles: str, custom_style: str, result: str) -> str:
        """Saves GenDocs payload and returns the UUID."""
        raise NotImplementedError
        
    @abstractmethod
    async def create_explain_history(self, code: str, styles: str, custom_style: str, result: str) -> str:
        """Saves Explain payload and returns the UUID."""
        raise NotImplementedError

    @abstractmethod
    async def get_docs_history(self, history_id: str) -> dict | None:
        """Retrieves a specific documentation generation record by UUID."""
        raise NotImplementedError

    @abstractmethod
    async def get_explain_history(self, history_id: str) -> dict | None:
        """Retrieves a specific explanation generation record by UUID."""
        raise NotImplementedError

    @abstractmethod
    async def get_all_docs_history(self) -> list:
        """Retrieves all docs history concisely mapped."""
        raise NotImplementedError

    @abstractmethod
    async def get_all_explain_history(self) -> list:
        """Retrieves all explain history concisely mapped."""
        raise NotImplementedError

    @abstractmethod
    async def clear_all_history(self) -> dict:
        """Deletes all database persistent records securely allowing fresh state."""
        raise NotImplementedError

    @abstractmethod
    async def delete_docs_history(self, history_id: str) -> bool:
        """Deletes precisely one generating history record safely by mapping UUID."""
        raise NotImplementedError

    @abstractmethod
    async def delete_explain_history(self, history_id: str) -> bool:
        """Deletes precisely one explanation history record securely by UUID."""
        raise NotImplementedError
