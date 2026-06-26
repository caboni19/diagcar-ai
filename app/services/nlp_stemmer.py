"""
DiagCar — Arabic Stemmer + Darija Spell Corrector  v2
======================================================
Conservative automotive-domain stemmer:
  يسخن → سخن   ·   المحرك → محرك   ·   الفرامل → فرامل
  يتوقف → وقف  ·   سخانة  → سخن
"""
import re
from functools import lru_cache
from typing import List

MIN_STEM = 3

# ─── Automotive root map (direct lookup — fastest & most accurate) ─────────
ROOT_MAP = {
    # heat
    'يسخن':'سخن','سخانة':'سخن','ساخن':'سخن','تسخين':'سخن','يتسخن':'سخن',
    'يسخونه':'سخن','سخنت':'سخن','مسخن':'سخن',
    # smoke
    'دخان':'دخن','يدخن':'دخن','دخنة':'دخن','مدخنة':'دخن','دخانة':'دخن',
    # engine
    'المحرك':'محرك','محركات':'محرك','للمحرك':'محرك',
    # stop / stall
    'يتوقف':'وقف','توقف':'وقف','توقفت':'وقف','يوقف':'وقف','وقوف':'وقف',
    'يقف':'وقف',
    # vibrate
    'يرتجف':'رجف','ارتجاف':'رجف','يرتعش':'رعش','رعشة':'رعش',
    'يهتز':'هتز','اهتزاز':'هتز','يرتعش':'رعش',
    # brake
    'الفرامل':'فرمل','فراملة':'فرمل','يفرمل':'فرمل','فرملة':'فرمل',
    # battery
    'البطارية':'بطري','البطاريات':'بطري',
    # start
    'يشتغل':'شغل','اشتغال':'شغل','يبدأ':'بدأ','تبدأ':'بدأ',
    # stall / choke
    'يخنق':'خنق','خنق':'خنق','اختناق':'خنق','خناق':'خنق',
    # smell
    'رائحة':'ريح','روائح':'ريح',
    # power
    'الطاقة':'طاقة','انقطع':'نقط',
    # injection
    'الحاقن':'حاقن','الحاقنات':'حاقن','حاقنات':'حاقن',
    # oil
    'الزيت':'زيت','زيوت':'زيت',
    # coolant / water
    'التبريد':'برد','مبرد':'برد','تبريد':'برد',
    # overheating
    'السخونة':'سخن','ارتفاع':'رفع',
}

# ─── Prefix list (longest first) ───────────────────────────────────────────
PREFIXES = ['بال','كال','فال','وال','لل','است','مست','ال','وب','وت','فل',
            'لت','لي','لب','ست','و','ف','ب','ل','ي','ت','ن','م']

# ─── Suffix list (longest first, conservative) ─────────────────────────────
SUFFIXES = ['وهم','وهن','وكم','ونا','تهم','تهن','تكم','تنا','يهم',
            'ات','ون','ين','ان','ها','هم','هن','كم','كن','نا','ني',
            'ية','ة','ي','ا','ن','و','ت','ه','ك']

def _normalise(w: str) -> str:
    w = re.sub(r'[\u064B-\u065F\u0670]','',w)   # diacritics
    w = re.sub(r'[أإآ]','ا',w)
    return w.replace('ى','ي').replace('ة','ه').replace('ؤ','و').replace('ئ','ي')

@lru_cache(maxsize=8192)
def stem_arabic(word: str) -> str:
    """
    Return stem of an Arabic word.
    Priority: direct root map → prefix/suffix stripping → original.
    """
    if not word or not re.search(r'[\u0600-\u06FF]', word):
        return word
    norm = _normalise(word)

    # 1. Direct map (most accurate for automotive domain)
    if word in ROOT_MAP:   return ROOT_MAP[word]
    if norm in ROOT_MAP:   return ROOT_MAP[norm]

    # 2. Greedy prefix strip
    w = norm
    for p in PREFIXES:
        if w.startswith(p) and len(w)-len(p) >= MIN_STEM:
            w = w[len(p):]; break

    # 3. Greedy suffix strip
    for s in SUFFIXES:
        if w.endswith(s) and len(w)-len(s) >= MIN_STEM:
            w = w[:-len(s)]; break

    return w if len(w) >= MIN_STEM else word

def stem_tokens(tokens: List[str]) -> List[str]:
    """Return original + stem for each token (richer TF-IDF coverage)."""
    out = []
    for t in tokens:
        out.append(t)
        s = stem_arabic(t)
        if s != t:
            out.append(s)
    return out

# ─────────────────────────────────────────────────────────────────────────────
# DARIJA / ARABIZI SPELL CORRECTOR
# ─────────────────────────────────────────────────────────────────────────────
_DARIJA_CANONICAL = {
    # smoke
    'dkhane','dkhana','dkhan',
    # heat
    'hanna','7anna','iskhane','skhana',
    # brake
    'frana','fren','frena',
    # battery
    'batterie','battri',
    # start/stop
    'tebda','yebda','twaqef','twaqaf','waqfet',
    # noise
    'sout','bruit',
    # vibration
    'rdua','rdwa',
    # stall
    'ykhnek','ikhnek','yokhnek',
    # fuel
    'lessance','essence','gasoil','gazwel',
    # oil
    'zit','lhuile','huile',
    # gearbox
    'boite','bwita',
    # accelerate/power
    'qowa','khsara',
    # injector
    'injecteur','injecteurs',
    # warning light
    'voyant','le voyant',
    # turbo
    'turbo',
    # abs
    'abs',
    # clutch
    'embrayage','debrayage',
    # overheating location
    'montees','montee','tla3a',
    # black
    'khal','khel',
    # engine
    'moteur','motor',
    # check engine
    'check engine','daw el moteur',
}

_DICT_SORTED = sorted(_DARIJA_CANONICAL, key=len, reverse=True)

@lru_cache(maxsize=4096)
def _lev(a: str, b: str) -> int:
    if a == b: return 0
    if not a: return len(b)
    if not b: return len(a)
    prev = list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        curr = [i]
        for j,cb in enumerate(b,1):
            curr.append(min(curr[j-1]+1, prev[j]+1, prev[j-1]+(ca!=cb)))
        prev = curr
    return prev[-1]

@lru_cache(maxsize=4096)
def correct_darija(word: str, max_dist: int = 2) -> str:
    w = word.lower().strip()
    if w in _DARIJA_CANONICAL: return w
    best, best_d = w, max_dist+1
    for can in _DICT_SORTED:
        if abs(len(w)-len(can)) > max_dist: continue
        d = _lev(w, can)
        if d < best_d:
            best_d, best = d, can
    return best if best_d <= max_dist else word

def correct_tokens(tokens: List[str]) -> List[str]:
    out = []
    for t in tokens:
        if re.match(r'^[a-zA-Z][a-zA-Z0-9]{2,}$', t):
            c = correct_darija(t)
            out.append(t)
            if c != t: out.append(c)
        else:
            out.append(t)
    return out

# ─────────────────────────────────────────────────────────────────────────────
# COMBINED PIPELINE
# ─────────────────────────────────────────────────────────────────────────────
def advanced_preprocess(tokens: List[str]) -> List[str]:
    """Spell-correct → stem → deduplicate."""
    step1 = correct_tokens(tokens)
    step2 = stem_tokens(step1)
    seen, out = set(), []
    for t in step2:
        if t not in seen:
            seen.add(t); out.append(t)
    return out
