from dataclasses import dataclass

@dataclass
class RouteDecision:
    path: str  # "rule", "short", "llm"
    intent: str
    confidence: float
    reason: str

def route(intent: str, confidence: float, settings) -> RouteDecision:
    if intent in {"saudacao", "despedida"} and confidence >= 0.5:
        return RouteDecision("rule", intent, confidence, "Regra simples para saudações/despedidas.")
    
    if confidence < settings.rule_confidence_threshold and intent in {"preco", "entrega", "transacao"}:
        return RouteDecision("llm", intent, confidence, "Intenção sensível; delega ao LLM.")
        
    if confidence >= settings.rule_confidence_threshold:
        return RouteDecision("short", intent, confidence, "Resposta curta automática baseada em intenção.")
        
    return RouteDecision("llm", intent, confidence, "Confiança baixa; pedir ao LLM.")