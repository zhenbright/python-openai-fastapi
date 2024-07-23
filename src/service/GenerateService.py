import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

class GenerateService:
    def __init__(self):
        self.client = OpenAI(api_key=api_key)
    
    def generate(
        self,
        service: str,
        promptText: str,
        pageAnalysis: str,
        pageResult: str,
        pageUseCase: str,
    ):
        response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},  # System message sets the behavior
                    {"role": "user", "content": "What is a LLM?"}  # User message is the query from the user
                ]
            )
        return response