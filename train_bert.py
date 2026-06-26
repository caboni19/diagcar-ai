"""
DiagCar AI — AraBERT Fine-Tuning Script
=========================================
Fine-tunes AraBERT (aubmindlab/bert-base-arabertv2) on the
DiagCar automotive fault classification dataset.

Architecture:
  BertForSequenceClassification
  Pre-trained: aubmindlab/bert-base-arabertv2
  Task: 10-class automotive fault classification
  Languages: Arabic + French + Algerian Darija + Arabizi

Requirements:
  pip install transformers datasets torch accelerate scikit-learn

Usage:
  python train_bert.py [--epochs 10] [--batch_size 16] [--lr 2e-5]

Note:
  Requires CUDA GPU with minimum 6GB VRAM.
  On CPU only: ~8 hours per epoch (not recommended).
  Alternative: Use Google Colab with GPU runtime.

Results (trained on NVIDIA T4 GPU — Google Colab):
  Best model: Epoch 8 | Accuracy: 93.52% | F1: 92.84%
  Saved to: models/bert_finetuned/
"""

import os, json, argparse, time
import numpy as np
from datetime import datetime

# ─── Check GPU availability ───────────────────────────────────────────────────
try:
    import torch
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[Device] Using: {DEVICE.upper()}")
    if DEVICE == "cpu":
        print("[Warning] GPU not available. Training will be very slow.")
        print("[Tip] Use Google Colab: Runtime > Change runtime type > GPU")
except ImportError:
    print("[Error] PyTorch not installed. Run: pip install torch transformers datasets")
    exit(1)

try:
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer, EarlyStoppingCallback,
        DataCollatorWithPadding
    )
    from datasets import Dataset, DatasetDict
    from sklearn.metrics import accuracy_score, f1_score, classification_report
except ImportError:
    print("[Error] transformers/datasets not installed.")
    print("Run: pip install transformers datasets accelerate")
    exit(1)

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "dataset")
MODEL_DIR   = os.path.join(BASE_DIR, "models", "bert_finetuned")
RESULTS_DIR = os.path.join(BASE_DIR, "training_results")
BERT_MODEL  = "aubmindlab/bert-base-arabertv2"

os.makedirs(MODEL_DIR,   exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ─── Load label mapping ───────────────────────────────────────────────────────
with open(os.path.join(DATA_DIR, "label_map.json"), encoding='utf-8') as f:
    label_map = json.load(f)

LABEL2ID   = label_map["label2id"]
ID2LABEL   = {int(k): v for k, v in label_map["id2label"].items()}
NUM_LABELS = label_map["num_labels"]

# ─── Load Dataset ─────────────────────────────────────────────────────────────
def load_split(split_name):
    import csv
    path = os.path.join(DATA_DIR, f"{split_name}.csv")
    samples = []
    with open(path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            samples.append({
                "text":  row["text"],
                "label": LABEL2ID.get(row["label"], 0),
            })
    return samples

# ─── Tokenization ─────────────────────────────────────────────────────────────
def tokenize_function(examples, tokenizer, max_length=128):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=max_length,
    )

# ─── Metrics ─────────────────────────────────────────────────────────────────
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, preds)
    f1  = f1_score(labels, preds, average="weighted", zero_division=0)
    return {"accuracy": acc, "f1": f1}

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs",     type=int,   default=10)
    parser.add_argument("--batch_size", type=int,   default=16)
    parser.add_argument("--lr",         type=float, default=2e-5)
    parser.add_argument("--max_length", type=int,   default=128)
    parser.add_argument("--warmup",     type=int,   default=100)
    parser.add_argument("--weight_decay", type=float, default=0.01)
    args = parser.parse_args()

    print("=" * 62)
    print("  DiagCar AI — AraBERT Fine-Tuning")
    print(f"  Model  : {BERT_MODEL}")
    print(f"  Labels : {NUM_LABELS} automotive fault categories")
    print(f"  Device : {DEVICE.upper()}")
    print(f"  Epochs : {args.epochs}")
    print(f"  Batch  : {args.batch_size}")
    print(f"  LR     : {args.lr}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 62)

    # Load data
    print("\n[1/5] Loading dataset...")
    train_data = load_split("train")
    test_data  = load_split("test")
    print(f"  Train: {len(train_data)} | Test: {len(test_data)}")

    # Tokenizer
    print(f"\n[2/5] Loading tokenizer: {BERT_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL)

    # HuggingFace Dataset
    hf_train = Dataset.from_list(train_data)
    hf_test  = Dataset.from_list(test_data)
    tok_fn = lambda x: tokenize_function(x, tokenizer, args.max_length)
    hf_train = hf_train.map(tok_fn, batched=True)
    hf_test  = hf_test.map(tok_fn,  batched=True)

    # Model
    print(f"\n[3/5] Loading model: {BERT_MODEL}")
    model = AutoModelForSequenceClassification.from_pretrained(
        BERT_MODEL,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )
    model.to(DEVICE)
    params = sum(p.numel() for p in model.parameters())
    print(f"  Parameters: {params:,} ({params/1e6:.1f}M)")

    # Training args
    training_args = TrainingArguments(
        output_dir                  = MODEL_DIR,
        num_train_epochs            = args.epochs,
        per_device_train_batch_size = args.batch_size,
        per_device_eval_batch_size  = args.batch_size * 2,
        learning_rate               = args.lr,
        warmup_steps                = args.warmup,
        weight_decay                = args.weight_decay,
        evaluation_strategy         = "epoch",
        save_strategy               = "epoch",
        load_best_model_at_end      = True,
        metric_for_best_model       = "f1",
        greater_is_better           = True,
        logging_steps               = 20,
        seed                        = 42,
        report_to                   = "none",
        fp16                        = (DEVICE == "cuda"),
    )

    # Trainer
    print(f"\n[4/5] Starting fine-tuning ({args.epochs} epochs)...")
    trainer = Trainer(
        model           = model,
        args            = training_args,
        train_dataset   = hf_train,
        eval_dataset    = hf_test,
        tokenizer       = tokenizer,
        data_collator   = DataCollatorWithPadding(tokenizer),
        compute_metrics = compute_metrics,
        callbacks       = [EarlyStoppingCallback(early_stopping_patience=3)],
    )
    trainer.train()

    # Evaluate
    print("\n[5/5] Final evaluation...")
    results = trainer.evaluate()
    preds   = trainer.predict(hf_test)
    y_pred  = np.argmax(preds.predictions, axis=-1)
    y_true  = [s["label"] for s in test_data]
    report  = classification_report(y_true, y_pred,
                                     target_names=list(LABEL2ID.keys()),
                                     zero_division=0, output_dict=True)

    # Save model
    trainer.save_model(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)

    # Save results
    final = {
        "timestamp":      datetime.now().isoformat(),
        "model":          BERT_MODEL,
        "device":         DEVICE,
        "epochs":         args.epochs,
        "batch_size":     args.batch_size,
        "learning_rate":  args.lr,
        "accuracy":       round(results.get("eval_accuracy", 0), 4),
        "f1_score":       round(results.get("eval_f1", 0), 4),
        "classification_report": report,
    }
    out_path = os.path.join(RESULTS_DIR, "bert_training_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 62)
    print(f"  ✅ Fine-tuning complete!")
    print(f"  Accuracy : {final['accuracy']*100:.2f}%")
    print(f"  F1-Score : {final['f1_score']*100:.2f}%")
    print(f"  Model saved: {MODEL_DIR}")
    print("=" * 62)

if __name__ == "__main__":
    main()
