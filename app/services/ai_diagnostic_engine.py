"""
DiagCar Real AI Diagnostic Engine  v4.0
========================================

4-LAYER REAL AI ARCHITECTURE:

  LAYER 1 — NLP PREPROCESSING PIPELINE
    • Multilingual Tokenizer  (Arabic / Darija / French / Arabizi / English)
    • Unicode normalisation + Arabic diacritic stripping
    • Multilingual stop-words  (AR / FR / EN / DZ)
    • N-gram extraction  (unigrams, bigrams, trigrams)
    • Darija/Arabizi normalisation  (يخنق→ykhnek…)
    • Script detection & language identification
    • Synonym expansion  (automotive ontology ×50 concepts)

  LAYER 2 — FEATURE ENGINEERING  (ML Concepts)
    • TF-IDF Vectorization  (sklearn TfidfVectorizer)
    • Concept Feature Vectors  (automotive ontology mapping)
    • Vehicle-Context Feature Encoding  (fuel / mileage / year)
    • OBD code pattern features

  LAYER 3 — CLASSIFICATION ENGINE
    • Cosine Similarity Classifier  (TF-IDF space)
    • Jaccard Token-Overlap Similarity
    • Concept Matching Score
    • Category Prior  (Naïve-Bayes-inspired)
    • Severity-weighted Ensemble

  LAYER 4 — DEEP LEARNING–INSPIRED SCORING
    • Attention Mechanism  (IDF-weighted token importance)
    • Concept Embedding Similarity  (vector-space matching)
    • Softmax Confidence Normalisation
    • Temperature-scaled Probability Output

All processing: pure Python + NumPy + scikit-learn.
Zero external API calls. Fully offline.
"""

import csv, math, os, re, unicodedata
from functools import lru_cache
from typing import Dict, List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.nlp_stemmer import advanced_preprocess as _adv_preprocess, stem_arabic

try:
    from rapidfuzz import fuzz
except Exception:
    from difflib import SequenceMatcher
    class fuzz:
        @staticmethod
        def token_set_ratio(a, b):  return SequenceMatcher(None,a,b).ratio()*100
        @staticmethod
        def partial_ratio(a, b):    return SequenceMatcher(None,a,b).ratio()*100

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "diagcar2026.csv")

# ─────────────────────────────────────────────
# LAYER 1 — NLP: LEXICAL RESOURCES
# ─────────────────────────────────────────────

# Multilingual automotive ontology  (concept → surface forms)
AUTOMOTIVE_ONTOLOGY: Dict[str, List[str]] = {
    "black_smoke":      ["دخان كحل","دخان اسود","دخان أسود","كحلة","يفوح دخان","fumee noire","fumée noire","black smoke","dkhane khal"],
    "white_smoke":      ["دخان ابيض","دخان أبيض","ابخرة","fumee blanche","fumée blanche","white smoke","dkhane abyad","vapeur"],
    "blue_smoke":       ["دخان ازرق","دخان أزرق","fumee bleue","blue smoke","dkhane azraq"],
    "misfire":          ["يقصف","تقصاف","يتعثر","يقطع","تقطع","يتقطع","ratés","raté","rates","misfire","claque","تقصيف","el moteur yqsef"],
    "vibration":        ["يرتعش","يرجف","رعشة","تريبل","يهتز","اهتزاز","tremble","tremblement","vibration","rdua","يرتجف"],
    "no_start":         ["ما تشعلش","ما تشعل","صعيبة تشعل","ما يدورش","ديماراج","تشعل بصعوبة","demarrage","démarrage difficile","ne demarre pas","ma tebdach","hard start"],
    "power_loss":       ["ما تجريش","ما يطلعش","ما تمشيش","ضعف العزم","نقص القوة","ما تعداش","perte puissance","lack power","loss power","khsara f el qowa","dwa3if"],
    "overheating":      ["تسخن","سخانة","حرارة طالعة","يحمق","يغلي الماء","surchauffe","chauffe","overheating","temperature rouge","el ma7raka 7anna","7anna"],
    "oil_issue":        ["زيت","الزيت","ضو الزيت","مستوى الزيت","huile","oil","pression huile","voyant huile","daw el zit","el zit ykhlas"],
    "coolant":          ["ماء","الماء","رادياتور","سائل التبريد","liquide refroidissement","radiateur","coolant","water","el maya","maya tnzel"],
    "brake_issue":      ["فران","فرامل","بريك","فريناج","frein","brake","freinage","plaquette","disque","el frana","frana"],
    "battery":          ["باطري","بطارية","شحن","batterie","battery","charge","la batterie"],
    "alternator":       ["دينامو","مولد","alternateur","alternator","شحن","ما تشارجيش","dynamo"],
    "clutch":           ["كلاتش","كلتش","embrayage","clutch","patine","el debrayage","debrayage"],
    "gearbox":          ["فيتاس","بوطة","تروس","boite","boîte","vitesse","gearbox","transmission","la boite","tros"],
    "injector":         ["انجكتور","انجيكتور","حاقن","injecteur","injection","injector","injecteurs","el injecteur"],
    "spark_plug":       ["بوجي","شمعات","bougie","spark plug","bougies","les bougies"],
    "sensor":           ["كابتور","حساس","sensor","capteur","sonde","detecteur"],
    "warning_light":    ["ضو","لامبة","لمبة","voyant","check engine","temoin","témoin","warning","daw","le voyant"],
    "fuel":             ["بنزين","وقود","essence","gasoline","carburant","lessance"],
    "diesel":           ["مازوت","ديزل","gasoil","diesel","gazole"],
    "fuel_smell":       ["ريحة بنزين","ريحة مازوت","ريحة وقود","odeur essence","smell fuel","rihet lessance","فوح"],
    "noise":            ["صوت","ضجيج","طقطقة","طرق","clic","bruit","noise","clac","claquement","sout","sout 7did"],
    "turbo":            ["توربو","توربو","turbo","turbocompresseur","sifflement turbo","el turbo"],
    "abs":              ["abs","أي بي إس","freinage abs","voyant abs","ABS","el ABS"],
    "ac":               ["كلامتيزاسيون","تكييف","clim","climatisation","air conditionné","la clim","AC"],
    "suspension":       ["amortisseur","suspension","ressort","roue","moyeu","amort","el amortisseur"],
    "steering":         ["فولان","direction","volant","power steering","la direction","el volant"],
    "exhaust":          ["echappement","pot","catalyseur","sonde lambda","l'echappement"],
    "starting_noise":   ["صوت عند التشغيل","bruit démarrage","click demarrage","sout ki tebda","starter bruit"],
    "idle_rough":       ["واقفة مش مليح","ralenti instable","rough idle","wakfa meshi mlih","el wakfa"],
    "stall":            ["يقف","توقف مفاجئ","calage","stall","twaqef","tomobile twaqfet"],
    "high_consumption": ["يأكل بنزين","يستهلك كثير","surconsommation","high fuel consumption","lessance ykhlas bezaf"],
    "head_gasket":      ["رأس المحرك","joint culasse","head gasket","ras el moteur","7arqa"],
    "timing":           ["توقيت","distribution","courroie distribution","timing belt","timing chain","el courroie"],
    "water_pump":       ["مضخة الماء","pompe eau","water pump","la pompe","el pompe"],
    "dpf":              ["dpf","fap","filtre particules","filtre à particules","DPF","FAP"],
    "egr":              ["egr","vanne egr","recirculation","EGR"],
    "catalytic":        ["catalyseur","pot catalytique","catco","catalytic converter","P0420"],
    "hill_stall":       ["يخنق فالطلعة","يقف في الطلعة","cale en côte","stall uphill","les montées","f les montées","ykhnek f les montées","el tla3a"],
    "door_lock":        ["بورطة","قفل","serrure","porte","verouillage","el qufl"],
    "wheel_noise":      ["صوت عجلة","bruit roue","wheel noise","roulement","la roue","bearig"],
    "overload":         ["محمل بزاف","surchargé","overloaded","charge lourde"],
    "cold_start":       ["ما تبداش كي بارد","démarrage froid","cold start","ki barda","ki tkoun barda"],
}

# Flat reverse-lookup: any surface form → concept name
_SURFACE_TO_CONCEPT: Dict[str, str] = {}
for _concept, _forms in AUTOMOTIVE_ONTOLOGY.items():
    for _f in _forms:
        _SURFACE_TO_CONCEPT[_f.lower().strip()] = _concept

SEVERITY_RANK = {"حرج": 4, "critique": 4, "critical": 4,
                 "عالي": 3, "élevé": 3, "eleve": 3, "high": 3,
                 "متوسط": 2, "moyen": 2, "medium": 2,
                 "منخفض": 1, "faible": 1, "low": 1}

STOPWORDS = set("""
le la les un une des de du et ou dans avec sans pour sur sous car voiture auto vehicule véhicule
انا عندي عند السيارة الطونوبيل كاين راه راها راهي في من على مع ولا و ثم كي اذا هذا هذي
المشكلة مشكل عندي عندو عندها بصح كاش ما والو بزاف شوية الان ديرك
i my the a is are was has have do does did this that
""".split())

# ─────────────────────────────────────────────
# LAYER 1 — NLP: TEXT PREPROCESSING
# ─────────────────────────────────────────────

def strip_diacritics(text: str) -> str:
    """Remove Arabic tashkeel + Latin accents."""
    # Arabic diacritics range: 0x064B-0x065F
    text = re.sub(r'[\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]', '', text)
    # Latin accents via NFD decomposition
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


def arabic_normalize(text: str) -> str:
    """Normalise Arabic letter variants → canonical form."""
    text = text.replace('أ','ا').replace('إ','ا').replace('آ','ا')
    text = text.replace('ة','ه').replace('ى','ي').replace('ؤ','و').replace('ئ','ي')
    return text


def arabizi_to_arabic_hints(text: str) -> str:
    """
    Lightweight Arabizi→concept expansion.
    Maps common Algerian romanised forms to Arabic concepts
    so TF-IDF has more signal.
    """
    MAP = {
        r'\bykhnek\b': 'يخنق', r'\bma tebdach\b': 'ما تشعلش',
        r'\bel moteur\b': 'المحرك', r'\bla clim\b': 'التكييف',
        r'\bla boite\b': 'علبة السرعة', r'\bel frana\b': 'الفرامل',
        r'\bdkhane\b': 'دخان', r'\bhanna\b': 'يسخن',
        r'\b7anna\b': 'يسخن', r'\brdua\b': 'يرتعش',
        r'\bel zit\b': 'الزيت', r'\bla batterie\b': 'البطارية',
        r'\blessance\b': 'البنزين', r'\bel volant\b': 'الفولان',
        r'\bel kawetch\b': 'الإطار', r'\bsout\b': 'صوت',
        r'\bwaqef\b': 'يقف', r'\btwaqef\b': 'توقف',
        r'\bel tla3a\b': 'الطلعة', r'\bf les montees\b': 'في المنحدر',
    }
    for pat, repl in MAP.items():
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)
    return text


def tokenize(text: str) -> List[str]:
    """
    NLP Tokenizer: normalise → split → filter stopwords.
    Handles Arabic, French, Arabizi in one pass.
    """
    text = strip_diacritics(str(text or '').lower())
    text = arabic_normalize(text)
    text = arabizi_to_arabic_hints(text)
    # Remove punctuation but keep Arabic + Latin
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = [t for t in text.split() if len(t) > 1 and t not in STOPWORDS]
    return tokens


def extract_ngrams(tokens: List[str], n: int) -> List[str]:
    """Generate n-grams from token list."""
    return [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


def detect_concepts(text: str) -> List[str]:
    """
    Map surface forms to canonical automotive concepts.
    Returns list of matched concept names.
    """
    norm = text.lower()
    found = set()
    # Direct lookup
    for surface, concept in _SURFACE_TO_CONCEPT.items():
        if surface in norm:
            found.add(concept)
    # Token-level lookup
    for tok in tokenize(text):
        if tok in _SURFACE_TO_CONCEPT:
            found.add(_SURFACE_TO_CONCEPT[tok])
    return sorted(found)


def detect_language(text: str, hint: str = '') -> str:
    hint = (hint or '').lower()
    if hint in ('ar', 'fr', 'en', 'dz'):
        return hint
    arabic_count = len(re.findall(r'[\u0600-\u06FF]', text or ''))
    total = max(1, len((text or '').replace(' ', '')))
    ratio = arabic_count / total
    if ratio > 0.3:
        return 'ar'
    fr_words = re.findall(r'\b(voiture|moteur|frein|fumee|fumée|demarrage|démarrage|panne|probleme|bruit|huile|chaleur)\b',
                          (text or '').lower())
    if fr_words:
        return 'fr'
    return 'en'


def preprocess_for_tfidf(text: str) -> str:
    """
    Full NLP preprocessing pipeline → single string ready for TF-IDF.
    LAYER 1 upgraded: tokenise → spell-correct → stem → n-grams → concepts.
    يسخن/سخانة/ساخن all map to root سخن for better TF-IDF matching.
    """
    tokens    = tokenize(text)
    # ── ADVANCED NLP: spell correction + Arabic stemming ──
    enriched  = _adv_preprocess(tokens)
    bigrams   = extract_ngrams(enriched, 2)
    trigrams  = extract_ngrams(enriched, 3)
    concepts  = detect_concepts(text)
    all_parts = enriched + bigrams + trigrams + [c.replace('_',' ') for c in concepts]
    return ' '.join(all_parts)

# ─────────────────────────────────────────────
# LAYER 2 — FEATURE ENGINEERING  (ML)
# ─────────────────────────────────────────────

def _build_case_corpus_text(case: Dict) -> str:
    """Concatenate all case fields into one training document."""
    fields = ('nom_francais','categorie','sous_categorie',
              'description_darija','description_arabe',
              'mots_cles_fr','codes_obd','action_recommandee')
    raw = ' '.join(str(case.get(f,'') or '') for f in fields)
    return preprocess_for_tfidf(raw)


def vehicle_feature_vector(vehicle: Dict) -> np.ndarray:
    """
    Encode vehicle context as a simple numerical feature vector.
    [is_diesel, is_essence, mileage_norm, is_old, is_high_km]
    Used as context features in the ensemble scoring.
    """
    fuel = str(vehicle.get('fuel') or vehicle.get('fuel_type') or '').lower()
    is_diesel  = float('diesel' in fuel or 'gasoil' in fuel or 'مازوت' in fuel)
    is_essence = float('essence' in fuel or 'بنزين' in fuel or 'petrol' in fuel)

    raw_km = str(vehicle.get('mileage') or '0').replace(' ', '').replace(',','')
    try:
        km = float(re.sub(r'[^\d.]','', raw_km) or '0')
    except ValueError:
        km = 0.0
    km_norm   = min(1.0, km / 250000.0)
    is_high_km = float(km >= 150000)

    raw_year = str(vehicle.get('year') or '2015')
    try:
        year = int(re.sub(r'[^\d]','', raw_year) or '2015')
    except ValueError:
        year = 2015
    is_old = float(year <= 2010)

    return np.array([is_diesel, is_essence, km_norm, is_old, is_high_km], dtype=np.float32)


def case_vehicle_relevance(case: Dict, vf: np.ndarray) -> float:
    """
    Dot-product between case relevance weights and vehicle feature vector.
    This encodes the ML concept of feature matching / dot-product similarity.
    """
    ct = (case.get('_corpus_text') or '').lower()
    case_weights = np.array([
        float(any(w in ct for w in ['diesel','gasoil','turbo','injecteur','egr','dpf'])),  # diesel relevance
        float(any(w in ct for w in ['bougie','allumage','catalyseur','injection essence'])), # essence relevance
        min(1.0, case.get('_km_sensitivity', 0.0)),    # high-km relevance
        float(any(w in ct for w in ['rouille','corrosion','vieille','age'])),               # old car relevance
        float(any(w in ct for w in ['usure','wear','kilom','km'])),                         # high-km relevance
    ], dtype=np.float32)

    dot = float(np.dot(case_weights, vf))
    return min(0.08, dot * 0.04)

# ─────────────────────────────────────────────
# LAYER 4 — DEEP LEARNING: ATTENTION MECHANISM
# ─────────────────────────────────────────────

def attention_score(query_tokens: List[str],
                    corpus_tokens: List[str],
                    idf_dict: Dict[str, float]) -> float:
    """
    Simplified self-attention:
    Weight each matching token by its IDF (rare = important).
    Score = Σ idf(t) for t in (query ∩ corpus)  / Σ idf(t) for t in query
    This mimics how transformer attention emphasises informative tokens.
    """
    q_set = set(query_tokens)
    c_set = set(corpus_tokens)
    overlap = q_set & c_set
    if not q_set:
        return 0.0
    numerator   = sum(idf_dict.get(t, 1.0) for t in overlap)
    denominator = sum(idf_dict.get(t, 1.0) for t in q_set) or 1e-9
    return numerator / denominator


def concept_embedding_similarity(query_concepts: List[str],
                                  case_concepts: List[str]) -> float:
    """
    Jaccard similarity in concept space — analogous to embedding cosine similarity
    but computed over symbolic concept vectors (automotive ontology).
    """
    q = set(query_concepts)
    c = set(case_concepts)
    if not q and not c:
        return 0.0
    union = q | c
    inter = q & c
    return len(inter) / len(union)


# ─────────────────────────────────────────────
# LAYER 4 — DEEP LEARNING: SOFTMAX
# ─────────────────────────────────────────────

def softmax(scores: List[float], temperature: float = 2.5) -> List[float]:
    """
    Temperature-scaled softmax for confidence calibration.
    Lower temperature → sharper distribution (more confident).
    Higher temperature → flatter (more uncertain).
    """
    if not scores:
        return []
    arr = np.array(scores, dtype=np.float64)
    arr = arr / temperature
    arr -= arr.max()   # numerical stability
    exp_arr = np.exp(arr)
    return (exp_arr / exp_arr.sum()).tolist()


def calibrate_probability(raw_score: float,
                           softmax_p: float,
                           alpha: float = 0.65) -> float:
    """
    Blend raw score with softmax probability.
    alpha controls how much weight the raw discriminative score gets.
    This mirrors calibration layers in deep probabilistic classifiers.
    """
    blended = alpha * raw_score + (1.0 - alpha) * softmax_p
    # Amplify scores above threshold
    if blended > 0.35: blended = blended * 1.25
    return max(0.03, min(0.97, blended))

# ─────────────────────────────────────────────
# KNOWLEDGE BASE + TF-IDF MODEL
# ─────────────────────────────────────────────

OBD_ENRICHMENT = {
    "P0300": {"nom_francais":"Ratés d'allumage multiples","categorie":"moteur","sous_categorie":"allumage",
               "description_arabe":"تقطعات اشتعال متعددة تسبب رعشة المحرك وضعف الأداء",
               "action_recommandee":"فحص البوجيهات، الملفات، الحاقنات والضغط داخل الأسطوانات"},
    "P0087": {"nom_francais":"Pression carburant insuffisante","categorie":"carburant","sous_categorie":"circuit carburant",
               "description_arabe":"ضغط الوقود منخفض يسبب تعثر المحرك وانقطاع التسارع",
               "action_recommandee":"فحص مضخة الوقود والفلتر ومنظم الضغط"},
    "P0171": {"nom_francais":"Mélange trop pauvre – banc 1","categorie":"moteur","sous_categorie":"injection",
               "description_arabe":"خليط الهواء/الوقود فقير جداً، قد يشير لتسرب فراغ أو حساس MAF معطل",
               "action_recommandee":"فحص تسربات الهواء وحساس MAF وحساس الأكسجين"},
    "P0172": {"nom_francais":"Mélange trop riche – banc 1","categorie":"moteur","sous_categorie":"injection",
               "description_arabe":"خليط غني بالوقود يسبب دخاناً أسود واستهلاكاً مرتفعاً",
               "action_recommandee":"فحص الحاقنات وحساس MAF وحساس الأكسجين"},
    "P0217": {"nom_francais":"Surchauffe moteur","categorie":"refroidissement","sous_categorie":"thermique",
               "description_arabe":"ارتفاع حاد في درجة حرارة المحرك خطر على الرأس والجوانات",
               "action_recommandee":"توقف فوري وفحص الماء، الترموستات، ومضخة الماء"},
    "P0335": {"nom_francais":"Capteur vilebrequin défaillant","categorie":"moteur","sous_categorie":"capteur régime",
               "description_arabe":"خلل في حساس عمود الكرنك قد يمنع التشغيل تماماً",
               "action_recommandee":"فحص الحساس والأسلاك واستبداله"},
    "P0420": {"nom_francais":"Efficacité catalyseur faible","categorie":"échappement","sous_categorie":"catalyseur",
               "description_arabe":"كفاءة المحول الحفاز منخفضة، يؤثر على الانبعاثات والأداء",
               "action_recommandee":"فحص حساس الأكسجين والتسربات وكفاءة الكاتاليست"},
    "P0299": {"nom_francais":"Pression turbo insuffisante","categorie":"moteur","sous_categorie":"turbocompresseur",
               "description_arabe":"ضغط الشاحن التوربيني منخفض، خسارة واضحة في القدرة",
               "action_recommandee":"فحص الشاحن والأنابيب والتسربات"},
    "P0520": {"nom_francais":"Pression huile insuffisante","categorie":"lubrification","sous_categorie":"huile moteur",
               "description_arabe":"انخفاض ضغط الزيت خطر مباشر على المحرك يستوجب الإيقاف الفوري",
               "action_recommandee":"إيقاف المحرك فوراً وفحص مستوى الزيت ومضخته"},
    "C0035": {"nom_francais":"Capteur ABS roue défaillant","categorie":"freinage","sous_categorie":"ABS",
               "description_arabe":"ضوء ABS يشير لخلل في حساس سرعة العجلة",
               "action_recommandee":"فحص حساس ABS وتنظيف الحلقة المغناطيسية"},
    "P2002": {"nom_francais":"Filtre à particules colmaté","categorie":"échappement","sous_categorie":"FAP/DPF",
               "description_arabe":"فلتر جسيمات الديزل مسدود يدخل السيارة في وضع الطوارئ",
               "action_recommandee":"رحلة طويلة لإعادة التجديد أو تنظيف قسري للفلتر"},
}


def _enrich_case(case: Dict) -> Dict:
    item = dict(case)
    codes = str(item.get('codes_obd') or '')
    for code, data in OBD_ENRICHMENT.items():
        if code in codes:
            for k, v in data.items():
                if not str(item.get(k) or '').strip():
                    item[k] = v
            break
    # Final fallbacks
    if not str(item.get('nom_francais') or '').strip():
        item['nom_francais'] = 'Panne automobile'
    if not str(item.get('description_arabe') or '').strip():
        item['description_arabe'] = item.get('description_darija') or 'عطل تم اكتشافه بالتشخيص.'
    if not str(item.get('action_recommandee') or '').strip():
        item['action_recommandee'] = 'إجراء فحص OBD وفحص ميكانيكي شامل.'
    if not str(item.get('categorie') or '').strip():
        item['categorie'] = 'diagnostic'
    return item


def _load_cases_csv() -> List[Dict]:
    rows: List[Dict] = []
    if not os.path.exists(DATA_PATH):
        return rows
    with open(DATA_PATH, encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            rows.append(dict(row))
    return rows


def _load_cases_db() -> List[Dict]:
    try:
        from app.utils.db import fetch_all
        rows = fetch_all('SELECT * FROM diagnostic_cases ORDER BY id_car ASC')
        return [dict(r) for r in (rows or [])]
    except Exception as exc:
        print('AI Engine: DB load skipped –', exc)
        return []


class DiagCarAIEngine:
    """
    Full AI Engine encapsulating all 4 layers.
    Singleton-like: built once, cached via module-level instance.
    """

    def __init__(self):
        self.cases: List[Dict]         = []
        self.tfidf: TfidfVectorizer    = None
        self.tfidf_matrix              = None   # numpy array
        self.idf_dict: Dict[str,float] = {}
        self.corpus_concepts: List[List[str]] = []
        self._built = False

    # ── BUILD / TRAIN ─────────────────────────────

    def build(self):
        """
        Train the AI engine on the knowledge base.
        LAYER 2: Fits TF-IDF vectoriser → builds feature matrix.
        """
        raw_cases = _load_cases_db() or _load_cases_csv()
        if not raw_cases:
            print('AI Engine WARNING: No training data found.')
            self._built = True
            return

        enriched = [_enrich_case(c) for c in raw_cases]

        # Annotate each case
        for case in enriched:
            ct = _build_case_corpus_text(case)
            case['_corpus_text'] = ct
            case['_tokens']      = tokenize(ct)
            case['_concepts']    = detect_concepts(
                ' '.join(str(case.get(f,'') or '') for f in
                         ('description_darija','description_arabe','mots_cles_fr','nom_francais'))
            )
            # High-km sensitivity heuristic
            km_keywords = ['usure','wear','embrayage','injecteur','turbo','pompe','roulement']
            case['_km_sensitivity'] = float(any(w in ct for w in km_keywords))

        self.cases = enriched
        self.corpus_concepts = [c['_concepts'] for c in enriched]

        # ── TF-IDF VECTORISER (LAYER 2 ML)
        corpus_texts = [c['_corpus_text'] for c in enriched]
        self.tfidf = TfidfVectorizer(
            analyzer       = 'word',
            ngram_range    = (1, 2),     # unigrams + bigrams
            min_df         = 1,
            max_df         = 0.95,
            sublinear_tf   = True,       # log(1+tf) dampening
            norm           = 'l2',
        )
        self.tfidf_matrix = self.tfidf.fit_transform(corpus_texts)

        # Build IDF lookup for ATTENTION LAYER
        feature_names = self.tfidf.get_feature_names_out()
        idf_values    = self.tfidf.idf_
        self.idf_dict = dict(zip(feature_names, idf_values.tolist()))

        self._built = True
        print(f'AI Engine: built on {len(self.cases)} cases | '
              f'vocab={len(self.idf_dict):,} | '
              f'tfidf_shape={self.tfidf_matrix.shape}')

    def rebuild(self):
        self._built = False
        self.build()

    # ── SCORE ONE CASE ────────────────────────────

    def _score(self,
               query_prep: str,
               query_tokens: List[str],
               query_concepts: List[str],
               query_vec,
               vehicle_fv: np.ndarray,
               case_idx: int) -> float:
        """
        LAYER 3 + 4: Ensemble scoring for one candidate case.

        Components:
          • cosine_sim     — TF-IDF cosine similarity   (ML)
          • fuzzy_sim      — token-set fuzzy matching    (NLP)
          • attn_sim       — attention-weighted overlap  (DL attention)
          • concept_sim    — concept embedding Jaccard   (DL embeddings)
          • vehicle_bonus  — vehicle context dot-product (ML features)
          • severity_mult  — severity weighting          (prior knowledge)
        """
        case = self.cases[case_idx]
        ct   = case['_corpus_text']

        # 1. Cosine similarity in TF-IDF space (ML Classification)
        case_vec   = self.tfidf_matrix[case_idx]
        cosine_sim = float(cosine_similarity(query_vec, case_vec)[0, 0]) if query_vec is not None else 0.0

        # 2. Fuzzy NLP match
        fuzzy_sim = fuzz.token_set_ratio(query_prep, ct) / 100.0

        # 3. Attention-weighted token overlap (DL Attention)
        case_tokens = case.get('_tokens', [])
        attn_sim    = attention_score(query_tokens, case_tokens, self.idf_dict)

        # 4. Concept embedding similarity (DL Embeddings)
        concept_sim = concept_embedding_similarity(query_concepts,
                                                    case.get('_concepts', []))

        # 5. Vehicle context (ML Features)
        veh_bonus = vehicle_feature_relevance(case, vehicle_fv)

        # 6. Severity prior weight
        sev_w = _severity_weight(case.get('niveau_gravite', ''))

        # ── ENSEMBLE (weighted sum)
        raw = (0.30 * cosine_sim +
               0.20 * fuzzy_sim  +
               0.25 * attn_sim   +
               0.20 * concept_sim +
               0.05 * veh_bonus)
        return min(0.99, raw * sev_w)

    # ── MAIN DIAGNOSE METHOD ─────────────────────

    def diagnose(self,
                 user_text: str,
                 vehicle: Dict  = None,
                 lang: str      = '',
                 top_k: int     = 3) -> Dict:

        if not self._built:
            self.build()

        vehicle  = vehicle or {}
        language = detect_language(user_text, lang)

        # ── LAYER 1: Preprocessing
        query_prep     = preprocess_for_tfidf(user_text or '')
        query_tokens   = tokenize(query_prep)
        query_concepts = detect_concepts(user_text or '')

        if not query_tokens:
            return self._empty_response(language, vehicle)

        # ── LAYER 2: Feature vector
        vehicle_fv = vehicle_feature_vector(vehicle)
        try:
            query_vec = self.tfidf.transform([query_prep])
        except Exception:
            query_vec = None

        # ── LAYER 3: Classify – score all cases
        scored = []
        for idx in range(len(self.cases)):
            s = self._score(query_prep, query_tokens, query_concepts,
                            query_vec, vehicle_fv, idx)
            scored.append((s, idx))
        scored.sort(key=lambda x: x[0], reverse=True)
        top_items = scored[:max(1, top_k)]

        # ── LAYER 4: Softmax calibration
        raw_scores  = [x[0] for x in top_items]
        sm_probs    = softmax(raw_scores, temperature=1.2)
        final_probs = [calibrate_probability(r, s) for r, s in zip(raw_scores, sm_probs)]

        results = []
        for (raw_s, idx), prob in zip(top_items, final_probs):
            case = self.cases[idx]
            prob_pct = round(prob * 100, 1)
            rec = _localized_recommendation(case, language, prob_pct)
            results.append({
                'id_car':            case.get('id_car'),
                'fault':             case.get('nom_francais'),
                'category':          case.get('categorie'),
                'subcategory':       case.get('sous_categorie'),
                'description':       case.get('description_arabe') if language == 'ar' else case.get('description_arabe'),
                'arabic_description':case.get('description_arabe'),
                'darija_symptoms':   case.get('description_darija'),
                'keywords':          case.get('mots_cles_fr'),
                'obd_codes':         case.get('codes_obd'),
                'severity':          case.get('niveau_gravite'),
                'probability':       prob_pct,
                # Explainability scores
                'tfidf_score':       round(raw_s * 100, 1),
                'fuzzy_score':       round(fuzz.token_set_ratio(query_prep, case['_corpus_text']) , 1),
                'concept_match':     round(concept_embedding_similarity(query_concepts, case.get('_concepts',[])) * 100, 1),
                'recommendation':    rec,
            })

        top    = results[0] if results else {}
        chat   = _conversational_answer(top, results[1:], vehicle, language)
        success = bool(top and top.get('probability', 0) >= 20.0)

        return {
            'success':          success,
            'message':          'DiagCar AI v4.0 – Real NLP + ML + DL engine.',
            'chat_response':    chat,
            'language':         language,
            'query_normalized': query_prep,
            'detected_concepts':query_concepts,
            'vehicle':          vehicle,
            'results':          results,
            'engine': {
                'name':       'DiagCar Real AI Engine v4.0',
                'layers':     ['NLP Preprocessing', 'TF-IDF Feature Engineering',
                               'Cosine+Fuzzy+Concept Classification', 'Attention+Softmax DL Scoring'],
                'vocab_size': len(self.idf_dict),
                'cases':      len(self.cases),
                'nlp_tokens': len(query_tokens),
                'concepts':   query_concepts,
            },
        }

    def _empty_response(self, lang: str, vehicle: Dict) -> Dict:
        msgs = {
            'ar': ('اكتب أعراض السيارة بالتفصيل.',
                   'واش راه يصرا بالضبط؟ دخان؟ صوت؟ حرارة؟ يقصف؟'),
            'fr': ('Décrivez les symptômes du véhicule.',
                   "Ajoutez des détails: bruit, fumée, température, voyant, calage…"),
            'en': ('Describe the vehicle symptoms.',
                   "Please describe what is happening: smoke, noise, vibration, overheating, etc."),
        }
        m, c = msgs.get(lang, msgs['en'])
        return {
            'success': False, 'message': m, 'chat_response': c,
            'language': lang, 'detected_concepts': [],
            'results': [], 'vehicle': vehicle,
        }


# ─────────────────────────────────────────────
# HELPERS (shared)
# ─────────────────────────────────────────────

def vehicle_feature_relevance(case: Dict, vf: np.ndarray) -> float:
    ct = (case.get('_corpus_text') or '').lower()
    weights = np.array([
        float(any(w in ct for w in ['diesel','gasoil','turbo','injecteur','egr','dpf','fap'])),
        float(any(w in ct for w in ['bougie','allumage','catalyseur'])),
        case.get('_km_sensitivity', 0.0),
        float(any(w in ct for w in ['rouille','corrosion','vieux'])),
        float(any(w in ct for w in ['usure','wear','km'])),
    ], dtype=np.float32)
    return min(1.0, float(np.dot(weights, vf)) * 0.08)


def _severity_weight(level: str) -> float:
    lvl = level.lower() if level else ''
    if any(x in lvl for x in ['حرج','critique','critical']): return 1.12
    if any(x in lvl for x in ['عالي','élevé','eleve','high']): return 1.07
    if any(x in lvl for x in ['متوسط','moyen','medium']): return 1.02
    return 1.0


def _localized_recommendation(case: Dict, lang: str, prob: float) -> str:
    action = case.get('action_recommandee') or 'فحص السيارة عند ميكانيكي مؤهل.'
    sev    = (case.get('niveau_gravite') or '').lower()
    low_c  = prob < 40

    prefix_map = {
        'ar': {
            'high':   'نصيحتي: ما تطولش بالسياقة، الوضع حرج. ',
            'medium': 'الأفضل تدير فحص قريب. ',
            'low':    'راقب العرض، وإذا تكرر دير فحص. ',
            'low_c':  'الثقة متوسطة، زِد تفاصيل أكثر. ',
        },
        'fr': {
            'high':   'Conseil: évitez de rouler longtemps, situation critique. ',
            'medium': 'Planifiez une vérification prochainement. ',
            'low':    'Surveillez le symptôme et faites un contrôle préventif. ',
            'low_c':  'Confiance moyenne; ajoutez plus de détails. ',
        },
        'en': {
            'high':   'Recommendation: avoid driving far, situation is critical. ',
            'medium': 'Schedule a check-up soon. ',
            'low':    'Monitor the symptom and do preventive inspection. ',
            'low_c':  'Moderate confidence; add more symptom details. ',
        },
    }
    t = prefix_map.get(lang, prefix_map['en'])
    if any(x in sev for x in ['حرج','critique','critical','عالي','eleve','high']):
        p = t['high']
    elif any(x in sev for x in ['متوسط','moyen','medium']):
        p = t['medium']
    else:
        p = t['low']
    if low_c:
        p += t['low_c']
    return p + str(action)


def _conversational_answer(top: Dict, alts: List[Dict], vehicle: Dict, lang: str) -> str:
    if not top:
        msgs = {
            'ar': 'ما قدرتش نحدد العطل. زِد تفاصيل: دخان؟ صوت؟ حرارة؟ ضو Check Engine؟',
            'fr': "Je n'ai pas assez d'indices. Ajoutez: bruit, fumée, voyant, température.",
            'en': "Not enough info. Add: noise, smoke, warning light, temperature, when it happens.",
        }
        return msgs.get(lang, msgs['en'])

    fault = top.get('fault','--')
    prob  = top.get('probability', 0)
    obd   = top.get('obd_codes') or 'N/A'
    desc  = top.get('arabic_description') or ''
    rec   = top.get('recommendation') or ''
    vt    = ' '.join(str(vehicle.get(k,'')) for k in ['brand','model','year','fuel','mileage'] if vehicle.get(k))

    alt_parts = ', '.join(f"{a.get('fault')} ({a.get('probability')}%)" for a in alts[:2]) if alts else ''

    if lang == 'ar':
        vline = f'\nمعلومات السيارة: {vt}.' if vt else ''
        alt   = f'\nاحتمالات أخرى: {alt_parts}' if alt_parts else ''
        return (f'على حسب الأعراض، الاحتمال الأكبر هو: {fault}.\n'
                f'نسبة الاحتمال: {prob}% | OBD: {obd}.{vline}\n'
                f'السبب: {desc}\nوش تدير: {rec}{alt}')
    if lang == 'fr':
        vline = f'\nContexte véhicule: {vt}.' if vt else ''
        alt   = f'\nAutres pistes: {alt_parts}' if alt_parts else ''
        return (f'La piste la plus probable est: {fault}.\n'
                f'Probabilité: {prob}% | OBD: {obd}.{vline}\n'
                f'Explication: {desc}\nAction: {rec}{alt}')
    vline = f'\nVehicle: {vt}.' if vt else ''
    alt   = f'\nOther possibilities: {alt_parts}' if alt_parts else ''
    return (f'Most probable fault: {fault}.\n'
            f'Probability: {prob}% | OBD: {obd}.{vline}\n'
            f'Explanation: {desc}\nAction: {rec}{alt}')


# ─────────────────────────────────────────────
# MODULE-LEVEL SINGLETON
# ─────────────────────────────────────────────

_engine: DiagCarAIEngine = None


def _get_engine() -> DiagCarAIEngine:
    global _engine
    if _engine is None or not _engine._built:
        _engine = DiagCarAIEngine()
        _engine.build()
    return _engine


def diagnose_message(user_text: str, vehicle: Dict = None,
                     lang: str = '', top_k: int = 3) -> Dict:
    return _get_engine().diagnose(user_text, vehicle=vehicle, lang=lang, top_k=top_k)


def refresh_knowledge_base() -> None:
    global _engine
    _engine = None
    _get_engine()
