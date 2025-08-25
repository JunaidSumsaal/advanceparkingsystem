import os
import joblib
import pandas as pd
from django.conf import settings
from sklearn.metrics import roc_auc_score, brier_score_loss, precision_score, confusion_matrix, classification_report
from .data_prep import build_full_dataset

MODEL_PATH = os.path.join(settings.BASE_DIR, "parking",
                          "ml", "model", "rf_spot_predictor.joblib")
CAT_COLS = ["spot_type"]
NUM_COLS = ["hour", "dow", "is_weekend", "ratio_15m", "ratio_60m",
            "changes_last_hour", "last_status", "active_booking", "price_per_hour"]
FEATURES = CAT_COLS + NUM_COLS


def evaluate_model():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found. Train first.")
        return

    df = build_full_dataset()
    if df.empty:
        print("❌ No data to evaluate.")
        return

    model = joblib.load(MODEL_PATH)
    X, y = df[FEATURES], df["label"]
    preds = model.predict_proba(X)[:, 1]
    pred_labels = (preds > 0.5).astype(int)

    if len(set(y)) < 2:
        print("⚠️ Only one class present. Reporting precision/confusion only.")
        prec = precision_score(y, pred_labels, zero_division=0)
        print(f"Precision@0.5: {prec:.4f}")
        print("Confusion Matrix:")
        print(confusion_matrix(y, pred_labels))
        return

    auc = roc_auc_score(y, preds)
    brier = brier_score_loss(y, preds)
    prec = precision_score(y, pred_labels, zero_division=0)
    print("📊 Evaluation")
    print(f"AUC: {auc:.4f}")
    print(f"Brier: {brier:.4f}")
    print(f"Precision@0.5: {prec:.4f}")
    print("Confusion Matrix:")
    print(confusion_matrix(y, pred_labels))
    print("\nClassification Report:")
    print(classification_report(y, pred_labels, zero_division=0))
