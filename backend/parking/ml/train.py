import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, brier_score_loss, precision_score
from parking.ml.data_prep import build_full_dataset
from django.conf import settings
import os
from datetime import datetime

MODEL_DIR = os.path.join(settings.BASE_DIR, "parking", "ml", "model")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "rf_spot_predictor.joblib")

def time_train_test_split(df, time_col="timestamp", test_fraction=0.2):
    df_sorted = df.sort_values(time_col)
    cutoff_index = int(len(df_sorted) * (1 - test_fraction))
    train = df_sorted.iloc[:cutoff_index]
    test = df_sorted.iloc[cutoff_index:]
    return train, test

def train_and_save():
    df = build_full_dataset()
    if df.empty:
        print("No data to train on")
        return

    cat_cols = ["spot_type"]
    num_cols = ["hour", "dow", "is_weekend", "ratio_15m", "ratio_60m", "changes_last_hour", "last_status", "active_booking", "price_per_hour"]
    features = cat_cols + num_cols

    train, test = time_train_test_split(df, "timestamp", test_fraction=0.2)
    X_train = train[features]
    y_train = train["label"]
    X_test = test[features]
    y_test = test["label"]

    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ], remainder="passthrough")

    clf = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42)
    pipeline = Pipeline([
        ("pre", preprocessor),
        ("clf", clf)
    ])

    pipeline.fit(X_train, y_train)

    preds = pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, preds)
    brier = brier_score_loss(y_test, preds)
    prec = precision_score(y_test, (preds > 0.5).astype(int))

    print(f"Trained model AUC={auc:.4f} brier={brier:.4f} prec@0.5={prec:.4f}")

    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")

if __name__ == "__main__":
    train_and_save()
