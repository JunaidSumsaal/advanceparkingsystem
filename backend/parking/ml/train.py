import os
import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, brier_score_loss, precision_score
from .data_prep import build_full_dataset

MODEL_DIR = os.path.join(settings.BASE_DIR, "parking", "ml", "model")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "rf_spot_predictor.joblib")

CAT_COLS = ["spot_type"]
NUM_COLS = ["hour", "dow", "is_weekend", "ratio_15m", "ratio_60m",
            "changes_last_hour", "last_status", "active_booking", "price_per_hour"]
FEATURES = CAT_COLS + NUM_COLS


def time_train_test_split(df, time_col="timestamp", test_fraction=0.2):
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    df_sorted = df.sort_values(time_col)
    cut = int(len(df_sorted) * (1 - test_fraction))
    if cut <= 0 or cut >= len(df_sorted):
        return df_sorted, pd.DataFrame()
    return df_sorted.iloc[:cut], df_sorted.iloc[cut:]


def train_and_save():
    print("🚀 Training predictor…")
    df = build_full_dataset()
    if df.empty:
        print("❌ No rows to train.")
        return None

    train, test = time_train_test_split(df, "timestamp", test_fraction=0.2)
    if train.empty or test.empty:
        print("⚠️ Not enough data to split; training on all data without test.")
        train, test = df, pd.DataFrame()

    X_train, y_train = train[FEATURES], train["label"]

    pre = ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS)],
        remainder="passthrough"
    )

    clf = RandomForestClassifier(
        n_estimators=250,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )

    pipe = Pipeline([("pre", pre), ("clf", clf)])
    pipe.fit(X_train, y_train)

    if not test.empty and len(set(test["label"])) >= 2:
        X_test, y_test = test[FEATURES], test["label"]
        preds = pipe.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, preds)
        brier = brier_score_loss(y_test, preds)
        prec = precision_score(y_test, (preds > 0.5).astype(int))
        print(f"✅ AUC={auc:.4f}  Brier={brier:.4f}  Prec@0.5={prec:.4f}")
    else:
        print("ℹ️ Skipping metrics: insufficient test class variety.")

    joblib.dump(pipe, MODEL_PATH)
    print(f"💾 Saved → {MODEL_PATH}")
    return MODEL_PATH
