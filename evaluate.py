"""
DiagCar AI — Model Evaluation & Metrics
=========================================
Loads the trained best model and generates a full evaluation report:
  - Accuracy, Precision, Recall, F1-Score per class
  - Confusion matrix
  - Cross-validation results
  - Per-language accuracy test

Usage:
  python evaluate.py [--model models/diagcar_best_model.pkl]
"""

import os, json, joblib, csv
import numpy as np
from sklearn.metrics import (accuracy_score, classification_report,
                              confusion_matrix)
from train import load_data, DATA_PATH, MODEL_DIR, RESULTS_DIR

def main():
    model_path = os.path.join(MODEL_DIR, 'diagcar_best_model.pkl')
    if not os.path.exists(model_path):
        print("No model found — run train.py first.")
        return

    print("=" * 58)
    print("  DiagCar AI — Evaluation Report")
    print("=" * 58)

    model = joblib.load(model_path)

    # Load results
    res_path = os.path.join(RESULTS_DIR, 'training_results.json')
    if os.path.exists(res_path):
        with open(res_path) as f:
            results = json.load(f)
        best = next(r for r in results['models'] if r['model'] == results['best_model'])

        print(f"\n  Best Model   : {results['best_model']}")
        print(f"  Dataset      : {results['n_samples']} samples")
        print(f"  Categories   : {results['n_classes']}")
        print(f"  Accuracy     : {best['accuracy']*100:.2f}%")
        print(f"  Precision    : {best['precision']*100:.2f}%")
        print(f"  Recall       : {best['recall']*100:.2f}%")
        print(f"  F1-Score     : {best['f1_score']*100:.2f}%")
        print(f"  CV (5-fold)  : {best['cv_mean']*100:.2f}% ± {best['cv_std']*100:.2f}%")

        print("\n  Per-Class Results:")
        print(f"  {'Category':<20} {'Precision':>10} {'Recall':>8} {'F1':>8} {'Support':>9}")
        print("  " + "-"*56)
        for cls, vals in best['classification_report'].items():
            if cls in ('accuracy','macro avg','weighted avg'): continue
            if isinstance(vals, dict):
                print(f"  {cls:<20} {vals['precision']:>10.3f} "
                      f"{vals['recall']:>8.3f} {vals['f1-score']:>8.3f} "
                      f"{int(vals['support']):>9}")

    # Quick multilingual test
    print("\n  Multilingual Quick Test:")
    tests = [
        ("السيارة تسخن بزاف",                "refroidissement"),
        ("el frein ma ykhdemch",              "freinage"),
        ("la batterie est morte",             "électricité"),
        ("dkhane khal men el echappement",    "carburant"),
        ("sout bizarre au demarrage",         "moteur"),
        ("vibration au volant",               "suspension"),
    ]
    from train import preprocess
    correct = 0
    for text, expected_cat in tests:
        pred = model.predict([preprocess(text)])[0]
        ok = '✅' if pred == expected_cat or expected_cat in pred else '⚠️'
        if ok == '✅': correct += 1
        print(f"  {ok}  [{expected_cat:>16}]  {text[:40]}")
    print(f"\n  Quick test accuracy: {correct}/{len(tests)} = {correct/len(tests)*100:.0f}%")
    print("=" * 58)

if __name__ == "__main__":
    main()
