import re
import unicodedata

SYNONYMS = {
    "voyant": ["lamp", "check", "temoin", "témoin", "ضو", "لمبة", "voyant"],
    "moteur": ["engine", "moteur", "motor", "محرك", "المحرك", "موتور"],
    "frein": ["frein", "brake", "فران", "فرامل", "بريك"],
    "huile": ["huile", "oil", "زيت", "الزيت"],
    "fumee": ["fumee", "fumée", "smoke", "دخان", "دخان اسود", "كحلة"],
    "essence": ["essence", "fuel", "carburant", "بنزين", "مازوت", "gasoil", "fuel"],
    "chauffe": ["chauffe", "surchauffe", "heat", "temperature", "سخانة", "تسخن", "حرارة"],
    "demarrage": ["demarrage", "démarrage", "start", "starter", "ديماراج", "تشغيل", "تشعل"],
    "batterie": ["batterie", "battery", "بطارية", "باطري"],
    "bruit": ["bruit", "noise", "son", "صوت", "طقطقة", "ضجيج"],
}


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = strip_accents(text.lower())
    text = re.sub(r"[\n\t]+", " ", text)
    text = re.sub(r"[^\w\s\u0600-\u06FF]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def expand_query(text: str) -> str:
    norm = normalize_text(text)
    additions = []
    for canonical, words in SYNONYMS.items():
        if any(normalize_text(w) in norm for w in words):
            additions.append(canonical)
            additions.extend(words)
    return normalize_text(norm + " " + " ".join(additions))
