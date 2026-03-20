from groq import Groq
from app.ports.llm_port import LLMPort
from app.core.config import settings

class GroqAdapter(LLMPort):
    """
    Adapter bridging our application to the external Groq API.
    This fulfills the LLMPort contract.
    """
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def generate_text(self, prompt: str = "", system_prompt: str = "", messages: list = None) -> str | dict:
        try:
            if messages:
                # Chat mode
                chat_completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
            else:
                # Standard prompt mode
                chat_completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )

            if hasattr(chat_completion, "choices") and len(chat_completion.choices) > 0:
                choice = chat_completion.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    return choice.message.content
                if hasattr(choice, "text"):
                    return choice.text

            return "No response from API"
        except Exception as e:
            return f"Error: {str(e)}"
