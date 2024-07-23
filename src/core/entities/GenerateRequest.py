from pydantic import BaseModel


class GenerateRequest(BaseModel):
    service: str