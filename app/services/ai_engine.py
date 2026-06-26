"""Compatibility wrapper for the upgraded DiagCar Hybrid AI engine."""
from app.services.ai_diagnostic_engine import diagnose_message, refresh_knowledge_base


def diagnose(user_text, vehicle=None, lang='', top_k=3):
    return diagnose_message(user_text=user_text, vehicle=vehicle or {}, lang=lang, top_k=top_k)


def train_model(force=False):
    refresh_knowledge_base()
    return True
