from fastapi import FastAPI
from pydantic import BaseModel
from api.clients.hf_openai_client import chat

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    max_tokens: int = 300
    temperature: float = 0.7
    top_p: float = 1.0

app = FastAPI()

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    text = chat([m.model_dump() for m in req.messages], max_tokens = req.max_tokens)
    return {"generated_text": text}