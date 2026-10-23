from pydantic import BaseModel

class Settings(BaseModel):
    ollama_model: str = "llama3"
    llm_temperature: float = 0.2
    rule_confidence_threshold: float = 0.6
    short_answer_max_tokens: int = 120
    # IMPORTANTE: Altere "postgres" e "sua_senha" para as suas credenciais reais do PostgreSQL
    db_conn_str: str = "postgresql://postgres:sua_senha@localhost:5432/dataplus_db"

SYSTEM_PROMPT = """Você é um agente corporativo seguro da DataPlus. 
- Seja claro e direto. 
- Utilize as informações com segurança. 
- Siga estritamente o esquema: 
RESPOSTA: <resposta ao usuário> 
RAZÃO: <1-2 linhas sobre como chegou à resposta>"""