import requests
from typing import List, Dict, Any
from configs import Settings, SYSTEM_PROMPT
from nlp import normalize, tokenize, remove_stop, detect_intent, extract_entities, summarize_short
from router import route
from database import registrar_auditoria

class HybridAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.history: List[Dict[str, str]] = []

    def _ollama_chat(self, messages: List[Dict[str, str]]) -> str:
        resp = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": self.settings.ollama_model,
                "messages": messages,
                "options": {"temperature": self.settings.llm_temperature}
            },
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]

    def respond(self, user_text: str) -> Dict[str, Any]:
        clean = normalize(user_text)
        tokens = tokenize(clean)
        tokens_ns = remove_stop(tokens)
        intent, conf, scores = detect_intent(user_text)
        slots = extract_entities(user_text)
        
        decision = route(intent, conf, self.settings)

        if decision.path == "rule":
            if intent == "saudacao":
                answer = "Olá! Bem-vindo à DataPlus. Como posso ajudar com segurança e dados?"
            elif intent == "despedida":
                answer = "Até mais! Protegendo seus dados com segurança."
            else:
                answer = "Certo!"
            
            result = {"answer": answer, "reason": decision.reason, "intent": intent, "confidence": conf, "slots": slots}
            self._remember(user_text, result["answer"])
            return result

        if decision.path == "short":
            if intent == "preco":
                answer = "Por favor, informe qual produto deseja consultar o valor."
            elif intent == "entrega":
                answer = "Informe seu CEP para calcularmos o prazo e o frete de forma segura."
            else:
                answer = summarize_short(user_text)
            
            result = {"answer": answer, "reason": decision.reason, "intent": intent, "confidence": conf, "slots": slots}
            self._remember(user_text, result["answer"])
            return result

        sys = {"role": "system", "content": SYSTEM_PROMPT}
        ctx = {
            "role": "user",
            "content": (
                f"Mensagem: {user_text}\n"
                f"Intenção: {intent} (conf={conf:.2f})\n"
                f"Entidades: {slots}\n"
                f"Histórico breve: {self._short_history()}\n"
                "Responda seguindo o esquema."
            )
        }
        
        try:
            llm_output = self._ollama_chat([sys, ctx])
            answer = self._extract_answer(llm_output)
            reason = self._extract_reason(llm_output)
        except Exception as e:
            answer = "Desculpe, o serviço de IA local (Ollama) está indisponível."
            reason = f"Erro de conexão com LLM: {str(e)}"

        result = {"answer": answer, "reason": reason, "intent": intent, "confidence": conf, "slots": slots}
        self._remember(user_text, result["answer"])
        
        # Registra auditoria da requisição no PostgreSQL
        registrar_auditoria(usuario_id=3, acao="CONSULTA_AGENTE", detalhes=f"Intenção: {intent}")
        
        return result

    def _short_history(self) -> str:
        return "\n".join([f"U:{h['user']} A:{h['assistant']}" for h in self.history[-3:]])

    def _remember(self, user_text: str, answer: str):
        self.history.append({"user": user_text, "assistant": answer})
        if len(self.history) > 20:
            self.history = self.history[-20:]

    @staticmethod
    def _extract_answer(text: str) -> str:
        import re
        m = re.search(r"RESPOSTA:\s*(.+?)(?:\n[A-Z_]+:|$)", text, flags=re.S)
        return m.group(1).strip() if m else text.strip()

    @staticmethod
    def _extract_reason(text: str) -> str:
        import re
        m = re.search(r"RAZÃO:\s*(.+?)(?:\n[A-Z_]+:|$)", text, flags=re.S)
        return m.group(1).strip() if m else "Roteamento para LLM."