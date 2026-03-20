from abc import ABC, abstractmethod

class LLMPort(ABC):
    """
    Port (Interface) for communicating with any Large Language Model.
    
    Beginners: Think of this as a contract. It says "I don't care if you use 
    Groq, OpenAI, or local Llama, as long as you give me a 'generate_text' function."
    This makes swapping AI models effortless later!
    """
    @abstractmethod
    def generate_text(self, prompt: str = "", system_prompt: str = "", messages: list = None) -> str | dict:
        raise NotImplementedError
