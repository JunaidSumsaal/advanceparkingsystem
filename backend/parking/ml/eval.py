import joblib
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss, precision_score, confusion_matrix, classification_report
from parking.ml.data_prep import build_full_dataset
from django.conf import settings
import os

MODEL_PATH = os.path.join(settings.BASE_DIR, "parking", "ml", "model", "rf_spot_predictor.joblib")

def evaluate_model():
    df = build_full_dataset()
    if df.empty:
        print("❌ No data available for evaluation")
        return

    cat_cols = ["spot_type"]
    num_cols = [
        "hour", "dow", "is_weekend",
        "ratio_15m", "ratio_60m", "changes_last_hour",
        "last_status", "active_booking", "price_per_hour"
    ]
    features = cat_cols + num_cols

    model = joblib.load(MODEL_PATH)

    X, y = df[features], df["label"]

    preds = model.predict_proba(X)[:, 1]
    pred_labels = (preds > 0.5).astype(int)

    # Metrics
    auc = roc_auc_score(y, preds) if len(set(y)) > 1 else "N/A"
    brier = brier_score_loss(y, preds) if len(set(y)) > 1 else "N/A"
    prec = precision_score(y, pred_labels, zero_division=0)
    cm = confusion_matrix(y, pred_labels)

    print("\n📊 Evaluation Results")
    print(f"AUC: {auc}")
    print(f"Brier Score: {brier}")
    print(f"Precision@0.5: {prec:.4f}")
    print("Confusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(classification_report(y, pred_labels, zero_division=0))
