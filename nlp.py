import re
import nltk
from nltk.corpus import stopwords
import spacy
from rapidfuzz import fuzz

try:
    nlp_spacy = spacy.load("pt_core_news_md")
except:
    nlp_spacy = None

try:
    STOP_PT = set(stopwords.words('portuguese'))
except:
    STOP_PT = set()

KEYWORDS = {
    "saudacao": {"oi", "olá", "boa tarde", "bom dia", "boa noite"},
    "despedida": {"tchau", "até mais", "valeu"},
    "preco": {"preço", "custa", "valor"},
    "entrega": {"entrega", "prazo", "frete"},
    "transacao": {"transacao", "extrato", "pagamento"}
}

REGEXES = {
    "email": re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b", flags=re.I),
    "cep": re.compile(r"\b\d{5}-?\d{3}\b"),
}

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

def tokenize(text: str):
    return [t for t in re.findall(r"\w+", text) if t.strip()]

def remove_stop(tokens):
    return [t for t in tokens if t not in STOP_PT]

def detect_intent(text: str):
    tx = normalize(text)
    scores = {}
    for intent, kws in KEYWORDS.items():
        score = max(fuzz.partial_ratio(tx, kw) for kw in kws)
        scores[intent] = score / 100.0
    best_intent = max(scores, key=scores.get)
    return best_intent, scores[best_intent], scores

def extract_entities(text: str):
    ents = []
    if nlp_spacy:
        doc = nlp_spacy(text)
        ents = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    
    regex_hits = {}
    for name, rx in REGEXES.items():
        m = rx.findall(text)
        if m:
            regex_hits[name] = m
            
    return {"spacy": ents, "regex": regex_hits}

def summarize_short(text: str):
    tx = normalize(text)
    return tx[:240]