from fastapi import FastAPI
from pydantic import BaseModel
from configs import Settings
from agent import HybridAgent

app = FastAPI(title="Agente DataPlus - Segurança e IA")
agent = HybridAgent(Settings())

class Query(BaseModel):
    text: str

@app.post("/chat")
def chat(q: Query):
    return agent.respond(q.text)