import json
from app.domain.schemas import DocumentationRequest
from app.ports.llm_port import LLMPort
from app.ports.history_port import HistoryPort

class DocumentationService:
    """
    Core Domain Logic layer. 
    It doesn't know about FastAPI API endpoints or the Groq library. 
    It just formats strings cleanly and uses the injected LLMPort contract.
    Beginners: This is where the core logic of your specific app goes!
    """
    def __init__(self, llm_client: LLMPort, history_client: HistoryPort = None):
        self.llm_client = llm_client
        self.history_client = history_client

    def build_prompts(self, request: DocumentationRequest):
        style_instructions = ""
        if request.styles:
            style_instructions = f"\nAPPLY THESE PRE-CONFIGURED STYLES AND TONES:\n" + "\n".join([f"- {s}" for s in request.styles])
            
        custom_ref_instructions = ""
        if request.custom_style:
            custom_ref_instructions = f"\nADAPT TO THIS CUSTOM FORMAT/TONE/STYLE REFERENCE:\n```\n{request.custom_style}\n```"

        if request.mode == "explain":
            system_prompt = "You are an elite, highly concise expert capable of breaking down complex code into simple, rich Markdown format explanations."
            prompt = f'''Generate a clear, completely Markdown-styled explanation for the following code snippet. Focus on helping developers understand the logic.

Code:
```
{request.code}
```
{style_instructions}{custom_ref_instructions}

Rules you must strictly follow:
1. Output a rich Markdown explanation of the code, its purpose, its inputs/outputs, and how it works step-by-step.
2. Do NOT output a single massive code block of the original code. Use Markdown headers (##), bold text (**), bullet points (-), and small inline code snippets (`code`) to break down the explanation clearly.
3. Create an explanation that helps a non-technical founder or new team member easily grasp the logic.
4. DO NOT provide conversational filler (e.g. "Here is the explanation..."). Output ONLY the final comprehensive markdown guide.
'''
        else:
            system_prompt = "You are an elite, highly concise coding assistant. Always respond with the code formatted in Markdown blocks. Detect the language automatically. Provide exactly the documented code block without introductory or concluding conversational text."
            prompt = f'''Generate clean, professional AI-powered documentation for the following code snippet. Focus on eliminating messy docs.

Code:
```
{request.code}
```
{style_instructions}{custom_ref_instructions}

Rules you must strictly follow:
1. Detect the language automatically from syntax (def → Python, function → JS/TS, fn → Rust, func → Go, etc.). Use the native Markdown block for that language.
2. Insert formatting/documentation immediately above the target (function, method, class) in the native doc standard (e.g. JSDoc for JS, Google Python Docstring for Python).
3. Do NOT break original indentation — shift documentation comments to align exactly with the code below it.
4. Output only the final fully-documented code in a single markdown fence. DO NOT provide conversational filler (e.g. "Here is the code...").

Required doc elements (unless requested otherwise by custom style):
- Clear one-paragraph description of purpose
- Name, type, and purpose of every parameter/argument
- Return value type and description
- Possible exceptions / errors raised

Now generate the standardized, clear, and uniform documented version of the provided code so learners or a small startup can immediately understand it.
'''
        return prompt, system_prompt

    async def generate_documentation(self, request: DocumentationRequest):
        prompt, system_prompt = self.build_prompts(request)
        result = self.llm_client.generate_text(prompt=prompt, system_prompt=system_prompt)
        
        saved_id = None
        if self.history_client:
            styles_str = json.dumps(request.styles)
            if request.mode == "explain":
                saved_id = await self.history_client.create_explain_history(
                    request.code, styles_str, request.custom_style, str(result)
                )
            else:
                saved_id = await self.history_client.create_generate_docs_history(
                    request.code, styles_str, request.custom_style, str(result)
                )

        return {
            "documentation": result, 
            "code_snippet": request.code, 
            "history_id": saved_id
        }
