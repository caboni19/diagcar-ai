"""
DiagCar AI — Model Training Pipeline
======================================
Trains and evaluates multiple NLP classifiers on the automotive fault dataset.
Saves the best model for production use in the diagnostic engine.

Models evaluated:
  1. TF-IDF + SVM (Linear SVC)         ← best for text classification
  2. TF-IDF + Random Forest
  3. TF-IDF + Naive Bayes (Multinomial)
  4. TF-IDF + Logistic Regression

Usage:
  python train.py [--data data/diagcar2026.csv] [--output models/]
"""

import os, sys, csv, json, time, re, argparse
import numpy as np
import joblib
import unicodedata
from datetime import datetime
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, classification_report, confusion_matrix)
from sklearn.preprocessing import LabelEncoder

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "data", "diagcar2026.csv")
MODEL_DIR  = os.path.join(BASE_DIR, "models")
RESULTS_DIR= os.path.join(BASE_DIR, "training_results")
SEED       = 42

os.makedirs(MODEL_DIR,   exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ─── NLP Preprocessing ────────────────────────────────────────────────────────
STOPWORDS = set("""
le la les un une des de du et ou dans avec sans pour sur sous
انا عندي عند السيارة الطونوبيل كاين راه في من على مع ولا و ثم كي
i my the a is are was has have do does
""".split())

def strip_diacritics(text):
    text = re.sub(r'[\u064B-\u065F\u0670]', '', str(text or ''))
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')

def arabic_normalize(text):
    text = text.replace('أ','ا').replace('إ','ا').replace('آ','ا')
    return text.replace('ة','ه').replace('ى','ي')

ARABIZI_MAP = {
    r'\bykhnek\b':'يخنق', r'\bma tebdach\b':'لا يشتغل',
    r'\bdkhane\b':'دخان', r'\b7anna\b':'يسخن',
    r'\brdua\b':'يرتجف', r'\bel moteur\b':'المحرك',
    r'\bla clim\b':'التكييف', r'\bla boite\b':'علبة السرعة',
    r'\bel frana\b':'الفرامل', r'\blessance\b':'البنزين',
    r'\bel zit\b':'الزيت', r'\bla batterie\b':'البطارية',
}

def preprocess(text):
    text = str(text or '').lower()
    text = strip_diacritics(text)
    text = arabic_normalize(text)
    for pat, repl in ARABIZI_MAP.items():
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    tokens = [t for t in text.split() if len(t) > 1 and t not in STOPWORDS]
    bigrams = [' '.join(tokens[i:i+2]) for i in range(len(tokens)-1)]
    return ' '.join(tokens + bigrams)

# ─── Load Dataset ─────────────────────────────────────────────────────────────
def load_data(path):
    samples, labels = [], []
    with open(path, encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            # Build combined feature text
            parts = [
                row.get('nom_francais',''),
                row.get('description_darija',''),
                row.get('description_arabe',''),
                row.get('mots_cles_fr',''),
                row.get('codes_obd',''),
            ]
            text = ' '.join(str(p) for p in parts if p)
            label = row.get('categorie','unknown').strip()
            if text and label:
                samples.append(preprocess(text))
                labels.append(label)
    return samples, labels

# ─── Model Definitions ────────────────────────────────────────────────────────
def get_pipelines():
    tfidf = TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True,
                            min_df=1, max_df=0.95, norm='l2')
    return {
        'SVM_LinearSVC': Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True,
                                      min_df=1, max_df=0.95, norm='l2')),
            ('clf', LinearSVC(C=1.0, max_iter=2000, random_state=SEED))
        ]),
        'RandomForest': Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True,
                                      min_df=1, max_df=0.95, norm='l2')),
            ('clf', RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=-1))
        ]),
        'NaiveBayes_MNB': Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1,2), sublinear_tf=False,
                                      min_df=1, max_df=0.95, norm=None,
                                      use_idf=False)),
            ('clf', MultinomialNB(alpha=0.1))
        ]),
        'LogisticRegression': Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True,
                                      min_df=1, max_df=0.95, norm='l2')),
            ('clf', LogisticRegression(C=5.0, max_iter=1000, random_state=SEED,
                                        solver='lbfgs'))
        ]),
    }

# ─── Training & Evaluation ────────────────────────────────────────────────────
def evaluate_model(name, pipeline, X_train, X_test, y_train, y_test, le):
    t0 = time.time()
    pipeline.fit(X_train, y_train)
    train_time = time.time() - t0

    y_pred = pipeline.predict(X_test)
    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec  = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1   = f1_score(y_test, y_pred, average='weighted', zero_division=0)

    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    X_all = X_train + X_test
    y_all = y_train + y_test
    cv_scores = cross_val_score(pipeline, X_all, y_all, cv=cv,
                                scoring='accuracy', n_jobs=-1)

    report = classification_report(y_test, y_pred, zero_division=0, output_dict=True)
    cm     = confusion_matrix(y_test, y_pred).tolist()

    return {
        'model':         name,
        'accuracy':      round(acc,  4),
        'precision':     round(prec, 4),
        'recall':        round(rec,  4),
        'f1_score':      round(f1,   4),
        'cv_mean':       round(cv_scores.mean(), 4),
        'cv_std':        round(cv_scores.std(),  4),
        'train_time_s':  round(train_time, 3),
        'classification_report': report,
        'confusion_matrix':      cm,
    }

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='DiagCar AI Training Pipeline')
    parser.add_argument('--data',   default=DATA_PATH)
    parser.add_argument('--output', default=MODEL_DIR)
    parser.add_argument('--test_size', type=float, default=0.20)
    args = parser.parse_args()

    print("=" * 62)
    print("  DiagCar AI — NLP Model Training Pipeline")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 62)

    # Load
    print(f"\n[1/4] Loading dataset: {args.data}")
    samples, labels = load_data(args.data)
    le = LabelEncoder()
    labels_enc = le.fit_transform(labels)

    label_counts = Counter(labels)
    print(f"  → {len(samples)} samples | {len(set(labels))} categories")
    print("  → Class distribution:")
    for lbl, cnt in sorted(label_counts.items(), key=lambda x: -x[1]):
        print(f"      {lbl:<25} {cnt:>4} samples")

    # Split
    print(f"\n[2/4] Splitting: {int((1-args.test_size)*100)}% train / {int(args.test_size*100)}% test")
    X_train, X_test, y_train, y_test = train_test_split(
        samples, labels, test_size=args.test_size,
        random_state=SEED, stratify=labels
    )
    print(f"  → Train: {len(X_train)} | Test: {len(X_test)}")

    # Train all models
    print("\n[3/4] Training and evaluating models...")
    pipelines = get_pipelines()
    results   = []
    best_f1   = -1
    best_name = None
    best_pipe = None

    for name, pipe in pipelines.items():
        print(f"  → {name}...", end=' ', flush=True)
        res = evaluate_model(name, pipe, X_train, X_test, y_train, y_test, le)
        results.append(res)
        print(f"Acc={res['accuracy']:.3f} | F1={res['f1_score']:.3f} "
              f"| CV={res['cv_mean']:.3f}±{res['cv_std']:.3f}")
        if res['f1_score'] > best_f1:
            best_f1   = res['f1_score']
            best_name = name
            best_pipe = pipe

    # Save best model
    print(f"\n[4/4] Best model: {best_name} (F1={best_f1:.4f})")
    model_path = os.path.join(args.output, 'diagcar_best_model.pkl')
    joblib.dump(best_pipe, model_path)
    print(f"  → Saved: {model_path}")

    # Save label encoder
    le_path = os.path.join(args.output, 'label_encoder.pkl')
    joblib.dump(le, le_path)

    # Save all results
    training_results = {
        'timestamp':    datetime.now().isoformat(),
        'dataset':      args.data,
        'n_samples':    len(samples),
        'n_classes':    len(set(labels)),
        'classes':      sorted(set(labels)),
        'test_size':    args.test_size,
        'best_model':   best_name,
        'best_f1':      best_f1,
        'models':       results,
    }
    res_path = os.path.join(RESULTS_DIR, 'training_results.json')
    with open(res_path, 'w', encoding='utf-8') as f:
        json.dump(training_results, f, ensure_ascii=False, indent=2)
    print(f"  → Results saved: {res_path}")

    # Summary table
    print("\n" + "=" * 62)
    print(f"  {'Model':<22} {'Acc':>6} {'Prec':>6} {'Rec':>6} {'F1':>6} {'CV':>10}")
    print("-" * 62)
    for r in sorted(results, key=lambda x: -x['f1_score']):
        star = "★" if r['model'] == best_name else " "
        print(f"  {star}{r['model']:<21} {r['accuracy']:>6.3f} "
              f"{r['precision']:>6.3f} {r['recall']:>6.3f} "
              f"{r['f1_score']:>6.3f} "
              f"{r['cv_mean']:>5.3f}±{r['cv_std']:.3f}")
    print("=" * 62)
    print(f"\n✅ Training complete — best model: {best_name}")
    return training_results

if __name__ == "__main__":
    main()
